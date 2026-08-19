from __future__ import annotations

import logging
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Self, cast

from group_assignment.datatypes import (
    CourseType,
    DegreeType,
    GroupCourseType,
    GroupDegreeType,
    GroupID,
    Score,
    StudentID,
    TeamID,
    TypeSelector,
)
from group_assignment.io import InputSchema

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Group:
    id: GroupID
    name: str = field(compare=False)
    capacity: int = field(compare=False)
    min_size: int = field(compare=False)
    course_type: GroupCourseType = field(compare=False)
    degree_type: GroupDegreeType = field(compare=False)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.min_size < 0:
            raise ValueError(
                f"Group {self.id}: min_size must be >= 0 (got {self.min_size})"
            )
        if self.capacity < self.min_size:
            raise ValueError(
                f"Group {self.id}: capacity must be >= min_size "
                f"(got capacity={self.capacity}, min_size={self.min_size})"
            )


@dataclass(frozen=True)
class Student:
    id: StudentID
    name: str = field(compare=False)
    course_type: CourseType = field(compare=False)
    degree_type: DegreeType = field(compare=False)
    type_specific_assignment: bool = field(compare=False)

    def accepted_by(self, group: Group) -> bool:
        return self.course_type.accepted_by(
            group.course_type
        ) and self.degree_type.accepted_by(group.degree_type)

    def matches(self, selector: TypeSelector | Student.Selector) -> bool:
        if (
            selector.course_type is not None
            and self.course_type != selector.course_type
        ):
            return False
        if (
            selector.degree_type is not None
            and self.degree_type != selector.degree_type
        ):
            return False
        return not (
            isinstance(selector, Student.Selector)
            and selector.type_specific_assignment is not None
            and self.type_specific_assignment != selector.type_specific_assignment
        )

    @dataclass(frozen=True)
    class Selector:
        course_type: CourseType | None = None
        degree_type: DegreeType | None = None
        type_specific_assignment: bool | None = None

        @classmethod
        def from_type_selector(
            cls,
            type_selector: TypeSelector,
            type_specific_assignment: bool | None = None,
        ) -> Self:
            return cls(
                course_type=type_selector.course_type,
                degree_type=type_selector.degree_type,
                type_specific_assignment=type_specific_assignment,
            )


@dataclass(frozen=True)
class Team:
    id: TeamID
    students: set[Student] = field(compare=False)
    rating: Mapping[Group, Score] = field(compare=False)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if len(self.students) == 0:
            raise ValueError(f"Team {self.id} has no students")
        if len(self.rating) == 0:
            raise ValueError(f"Team {self.id} rating is empty")
        for group, score in self.rating.items():
            if score < 0:
                raise ValueError(
                    f"Team {self.id} has negative score {score} for group {group.id}"
                )
            if not self.accepted_by(group):
                raise ValueError(
                    f"Team {self.id} has score for group {group.id} that does not "
                    "accept all team members"
                )

    @property
    def size(self) -> int:
        return len(self.students)

    def num_students(
        self,
        selector: TypeSelector
        | Student.Selector
        | Collection[TypeSelector | Student.Selector]
        | None = None,
    ) -> int:
        if selector is None:
            return self.size
        selectors = (
            (selector,)
            if isinstance(selector, (TypeSelector, Student.Selector))
            else selector
        )
        return sum(1 for s in self.students if any(s.matches(sel) for sel in selectors))

    def accepted_by(self, group: Group) -> bool:
        return all(s.accepted_by(group) for s in self.students)


@dataclass(frozen=True)
class Input:
    _groups: Mapping[GroupID, Group]
    _students: Mapping[StudentID, Student]
    _teams: Mapping[TeamID, Team]

    @property
    def groups(self) -> Iterable[Group]:
        return self._groups.values()

    @property
    def students(self) -> Iterable[Student]:
        return self._students.values()

    @property
    def teams(self) -> Iterable[Team]:
        return self._teams.values()

    def group(self, group_id: GroupID) -> Group:
        return self._groups[group_id]

    def student(self, student_id: StudentID) -> Student:
        return self._students[student_id]

    def team(self, team_id: TeamID) -> Team:
        return self._teams[team_id]

    @classmethod
    def build_from_input_schema(cls, io_model: InputSchema) -> Self:
        logger.info("Building Input from InputSchema")

        groups: Mapping[GroupID, Group] = {
            gid: Group(
                id=gid,
                name=g.name,
                capacity=g.capacity,
                min_size=g.min_size,
                course_type=g.course_type,
                degree_type=g.degree_type,
            )
            for gid, g in io_model.groups.items()
        }

        students: dict[StudentID, Student] = {}
        for sid, s in io_model.students.items():
            if s.course_type == CourseType.CDS and s.degree_type == DegreeType.MASTER:
                logger.warning(
                    f"Student {sid} has invalid combination "
                    f"{CourseType.CDS.value} {DegreeType.MASTER.value} "
                    f"-> assuming {DegreeType.BACHELOR.value}"
                )
                degree_type = DegreeType.BACHELOR
            elif (
                s.course_type == CourseType.COMPSCI
                and s.degree_type == DegreeType.BACHELOR
            ):
                logger.warning(
                    f"Student {sid} has invalid combination "
                    f"{CourseType.COMPSCI.value} {DegreeType.BACHELOR.value} "
                    f"-> assuming {DegreeType.MASTER.value}"
                )
                degree_type = DegreeType.MASTER
            else:
                degree_type = s.degree_type

            students[sid] = Student(
                id=sid,
                name=s.name,
                course_type=s.course_type,
                degree_type=degree_type,
                type_specific_assignment=s.type_specific_assignment,
            )

        def normalize_rating(rating: dict[Group, Score]) -> dict[Group, Score]:
            unique_scores = sorted(set(rating.values()))
            score_to_rank = {
                score: cast("Score", rank) for rank, score in enumerate(unique_scores)
            }
            return {g: score_to_rank[score] for g, score in rating.items()}

        invalid_scores = 0
        teams: dict[TeamID, Team] = {}
        for tid, team_sids in io_model.teams.items():
            team_students = {students[sid] for sid in team_sids}

            if len(io_model.ratings[tid]) == 0:
                raise ValueError(f"Team {tid} has empty rating")

            rating: dict[Group, Score] = {}
            for gid, score in io_model.ratings[tid].items():
                g = groups[gid]
                if all(s.accepted_by(g) for s in team_students):
                    rating[g] = score
                else:
                    invalid_scores += 1
                    logger.debug(
                        f"Removed group {g.id} from rating of team {tid} because not "
                        f"all team members are accepted by the group"
                    )
            rating = normalize_rating(rating)

            if len(rating) == 0:
                logger.error(
                    f"Team {tid} has empty rating after removing groups that do not "
                    f"accept all team members. Removing team and students {team_sids}."
                )
                for sid in team_sids:
                    del students[sid]
                continue

            teams[tid] = Team(id=tid, students=team_students, rating=rating)

        if invalid_scores > 0:
            logger.warning(
                f"Removed {invalid_scores} groups from team ratings because not all "
                f"team members are accepted by the group"
            )

        return cls(groups, students, teams)
