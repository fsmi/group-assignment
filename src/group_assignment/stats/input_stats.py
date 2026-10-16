from group_assignment.datatypes import (
    CourseType,
    DegreeType,
    GroupID,
    Score,
    StudentTypeSelector,
)
from group_assignment.model import Input


def count_students_by_type(
    inp: Input, selector: StudentTypeSelector | None = None
) -> dict[tuple[CourseType, DegreeType], int]:
    student_counts = {
        (course_type, degree_type): 0
        for course_type in CourseType
        for degree_type in DegreeType
    }
    for student in inp.students:
        if selector is not None and not student.matches(selector):
            continue
        student_counts[(student.course_type, student.degree_type)] += 1
    return student_counts


def count_tsa_students(inp: Input) -> int:
    return sum(1 for student in inp.students if student.type_specific_assignment)


def aggregate_ratings_by_groups(inp: Input) -> dict[Score, dict[GroupID, int]]:
    scores = sorted({score for team in inp.teams for score in team.rating.values()})
    scores_by_group = {score: {group.id: 0 for group in inp.groups} for score in scores}
    for team in inp.teams:
        for group, score in team.rating.items():
            scores_by_group[score][group.id] += team.size
    return scores_by_group


def sum_group_min_sizes(inp: Input) -> int:
    return sum(group.min_size for group in inp.groups)


def sum_group_capacities(inp: Input) -> int:
    return sum(group.capacity for group in inp.groups)
