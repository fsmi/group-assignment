import logging
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Self

from group_assignment.datatypes import GroupID, StudentTypeSelector, TeamID
from group_assignment.io import OutputSchema

from .input import Group, Input, Student, Team

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Assignment:
    _assignment: dict[Team, Group]

    def group_of_team(self, team: Team) -> Group:
        return self._assignment[team]

    def groups_to_students(self) -> Mapping[Group, set[Student]]:
        groups_to_students: dict[Group, set[Student]] = {}
        for team, group in self._assignment.items():
            if group not in groups_to_students:
                groups_to_students[group] = set()
            groups_to_students[group].update(team.students)
        return groups_to_students

    def students_assigned_to_group(self, group: Group) -> set[Student]:
        return {
            student
            for t, g in self._assignment.items()
            if g == group
            for student in t.students
        }

    def num_students_assigned_to_group(
        self,
        group: Group,
        selector: StudentTypeSelector
        | Student.Selector
        | Collection[StudentTypeSelector | Student.Selector],
    ) -> int:
        return sum(
            t.num_students(selector) for t, g in self._assignment.items() if g == group
        )

    @classmethod
    def build_from_id_mapping(
        cls, mapping: Mapping[TeamID, GroupID], inp: Input
    ) -> Self:
        logger.info("Building Assignment from TeamID -> GroupID mapping")
        assignment = {inp.team(tid): inp.group(gid) for tid, gid in mapping.items()}
        return cls(assignment)

    @classmethod
    def build_from_output_schema(cls, output_schema: OutputSchema, inp: Input) -> Self:
        logger.info("Building Assignment from OutputSchema")
        return cls.build_from_id_mapping(output_schema.root, inp)

    def to_output_schema(self) -> OutputSchema:
        logger.info("Building OutputSchema from Assignment")
        id_mapping = {t.id: g.id for t, g in self._assignment.items()}
        return OutputSchema(id_mapping)
