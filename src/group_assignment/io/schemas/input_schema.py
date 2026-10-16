from collections import defaultdict
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from group_assignment.datatypes import (
    CourseType,
    DegreeType,
    GroupCourseType,
    GroupDegreeType,
    GroupID,
    Score,
    StudentID,
    TeamID,
)


class Group(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    capacity: int
    min_size: int
    course_type: GroupCourseType
    degree_type: GroupDegreeType


class Student(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    course_type: CourseType
    degree_type: DegreeType
    not_fluent_in_german: bool = False
    type_specific_assignment: bool


Team = set[StudentID]


Rating = dict[GroupID, Score]


class InputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groups: dict[GroupID, Group]
    students: dict[StudentID, Student]
    teams: dict[TeamID, Team]
    ratings: dict[TeamID, Rating]

    @model_validator(mode="after")
    def validate_teams(self) -> Self:
        student_to_teams: dict[StudentID, list[TeamID]] = defaultdict(list)

        # validate that all team members are known students
        for tid, t in self.teams.items():
            for sid in t:
                if sid not in self.students:
                    raise ValueError(f"Unknown student {sid} in team {tid}")

                student_to_teams[sid].append(tid)

        # validate that all students are assigned to exactly one team
        for sid in self.students:
            tids = student_to_teams.get(sid, [])
            if not tids:
                raise ValueError(f"Student {sid} is not assigned to any team")
            if len(tids) > 1:
                raise ValueError(f"Student {sid} assigned to multiple teams: {tids}")

        return self

    @model_validator(mode="after")
    def validate_ratings(self) -> Self:
        # validate that for each team a rating is provided
        teams_without_ratings = set(self.teams.keys()) - set(self.ratings.keys())
        if teams_without_ratings:
            raise ValueError(f"No rating for team {teams_without_ratings.pop()}")

        # validate that each rating is for a known team
        unknown_teams_with_rating = set(self.ratings.keys()) - set(self.teams.keys())
        if unknown_teams_with_rating:
            raise ValueError(
                f"Rating for unknown team {unknown_teams_with_rating.pop()}"
            )

        # validate that ratings only contain known groups
        for tid, rating in self.ratings.items():
            for gid in rating:
                if gid not in self.groups:
                    raise ValueError(
                        f"Rating for team {tid} contains unknown group {gid}"
                    )

        return self
