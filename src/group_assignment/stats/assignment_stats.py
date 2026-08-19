from collections import defaultdict
from collections.abc import Mapping

from group_assignment.datatypes import (
    CourseType,
    DegreeType,
    GroupID,
    Score,
    TypeSelector,
)
from group_assignment.model import Assignment, Input, Student


def count_students_by_group(
    inp: Input, assignment: Assignment
) -> Mapping[GroupID, int]:
    counts = {group.id: 0 for group in inp.groups}
    for team in inp.teams:
        group = assignment.group_of_team(team)
        counts[group.id] += team.size
    return counts


def aggregate_assignment_scores(
    inp: Input, assignment: Assignment, selector: Student.Selector | None = None
) -> Mapping[Score, int]:
    scores = sorted({score for team in inp.teams for score in team.rating.values()})
    student_count_by_score = dict.fromkeys(scores, 0)
    for team in inp.teams:
        group = assignment.group_of_team(team)
        if group in team.rating:
            student_count_by_score[team.rating[group]] += team.num_students(selector)
    return student_count_by_score


def aggregate_assignment_scores_by_group(
    inp: Input, assignment: Assignment
) -> dict[Score, dict[GroupID, int]]:
    scores = sorted({score for team in inp.teams for score in team.rating.values()})
    student_count_by_group_by_score = {
        score: {group.id: 0 for group in inp.groups} for score in scores
    }
    for team in inp.teams:
        group = assignment.group_of_team(team)
        score = team.rating[group]
        student_count_by_group_by_score[score][group.id] += team.size
    return student_count_by_group_by_score


def count_tsa_students_by_type_count_in_groups(
    inp: Input, assignment: Assignment, selector: TypeSelector
) -> Mapping[int, int]:
    r: dict[int, int] = defaultdict(int)
    for group in inp.groups:
        num_tsa_students = assignment.num_students_assigned_to_group(
            group,
            Student.Selector.from_type_selector(
                selector, type_specific_assignment=True
            ),
        )
        num_type_specific_students = assignment.num_students_assigned_to_group(
            group,
            Student.Selector.from_type_selector(selector),
        )
        if num_tsa_students > 0:
            r[num_type_specific_students] += num_tsa_students
    return r


def count_students_in_group_by_type(
    inp: Input, assignment: Assignment, group_id: GroupID
) -> dict[tuple[CourseType, DegreeType], int]:
    counts = {
        (course_type, degree_type): 0
        for course_type in CourseType
        for degree_type in DegreeType
    }
    for student in assignment.students_assigned_to_group(inp.group(group_id)):
        counts[(student.course_type, student.degree_type)] += 1
    return counts
