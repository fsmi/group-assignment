from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

GroupID = NewType("GroupID", str)
StudentID = NewType("StudentID", str)
TeamID = NewType("TeamID", str)


Score = NewType("Score", int)


class CourseType(StrEnum):
    INFO = "info"
    COMPSCI = "compsci"
    MATHE = "mathe"
    CDS = "cds"
    LEHRAMT = "lehramt"

    def accepted_by(self, group_course_type: GroupCourseType) -> bool:
        return group_course_type.accepts(self)


class GroupCourseType(StrEnum):
    INFO = CourseType.INFO.value
    COMPSCI = CourseType.COMPSCI.value
    MATHE = CourseType.MATHE.value
    CDS = CourseType.CDS.value
    LEHRAMT = CourseType.LEHRAMT.value
    ANY = "any"

    def accepts(self, course_type: CourseType) -> bool:
        return self == GroupCourseType.ANY or self.value == course_type.value


class DegreeType(StrEnum):
    BACHELOR = "bachelor"
    MASTER = "master"

    def accepted_by(self, group_degree_type: GroupDegreeType) -> bool:
        return group_degree_type.accepts(self)


class GroupDegreeType(StrEnum):
    BACHELOR = DegreeType.BACHELOR.value
    MASTER = DegreeType.MASTER.value
    ANY = "any"

    def accepts(self, degree_type: DegreeType) -> bool:
        return self == GroupDegreeType.ANY or self.value == degree_type.value


@dataclass(frozen=True)
class TypeSelector:
    course_type: CourseType | None = None
    degree_type: DegreeType | None = None
