import rich
from rich.align import Align
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from group_assignment.cp import Config
from group_assignment.cp.config import MinNumStudents
from group_assignment.datatypes import (
    INVALID_COURSE_DEGREE_COMBINATIONS,
    CourseType,
    DegreeType,
    StudentTypeSelector,
)
from group_assignment.model import Assignment, Input, Student

from .assignment_stats import (
    aggregate_assignment_scores,
    aggregate_assignment_scores_by_group,
    count_students_by_group,
    count_students_by_type_count_in_groups,
)

# scores from which on an assignment is shown as bad (red)
MIN_BAD_SCORE = 2


def _fmt_score_count(score: int, count: int) -> Text | str:
    # students with a bad score are shown in red
    if score >= MIN_BAD_SCORE and count > 0:
        return Text(str(count), style="red")
    return str(count)


def print_assignment_summary(
    inp: Input, assignment: Assignment, config: Config | None = None
) -> None:
    tables = [
        build_group_stats_table(inp, assignment),
        build_acc_scores_table(inp, assignment),
    ]
    if config is not None:
        tables.extend(
            build_same_type_assignment_table(inp, assignment, constraints, tsa_only)
            for constraints, tsa_only in (
                (config.min_num_students_tsa, True),
                (config.min_num_students_all, False),
            )
            if constraints
        )
    # blank line above each table
    panel = Panel(
        Group(*(Align.center(Padding(table, (1, 0, 0, 0))) for table in tables)),
        title="Assignment",
        expand=False,
    )
    rich.print(panel)


def build_acc_scores_table(inp: Input, assignment: Assignment) -> Table:
    scores = aggregate_assignment_scores(inp, assignment)

    table = Table(title="Scores")
    table.add_column("Types")
    table.add_column("TSA")
    for score in scores:
        table.add_column(f"{score}", justify="right")

    def add_rows(
        label: str,
        course_type: CourseType | None,
        degree_type: DegreeType | None,
        style: str,
    ) -> None:
        # one row each for non-TSA and TSA students
        for i, tsa in enumerate((False, True)):
            counts = aggregate_assignment_scores(
                inp,
                assignment,
                Student.Selector(
                    course_type=course_type,
                    degree_type=degree_type,
                    type_specific_assignment=tsa,
                ),
            )
            table.add_row(
                label if i == 0 else "",
                Text(str(tsa).lower(), style="not bold"),
                *(_fmt_score_count(score, counts[score]) for score in scores),
                style=style,
            )

    table.add_row(
        "all",
        "",
        *(_fmt_score_count(score, scores[score]) for score in scores),
        style="bold",
    )
    add_rows("", None, None, style="bold")
    table.add_section()

    # alternating background per course/degree type
    types = [
        (course_type, degree_type)
        for course_type in CourseType
        for degree_type in DegreeType
        if (course_type, degree_type) not in INVALID_COURSE_DEGREE_COMBINATIONS
    ]
    for i, (course_type, degree_type) in enumerate(types):
        add_rows(
            f"{course_type.value} {degree_type.value}",
            course_type,
            degree_type,
            style="" if i % 2 == 0 else "on grey19",
        )

    return table


def build_group_stats_table(inp: Input, assignment: Assignment) -> Table:
    students_by_group = count_students_by_group(inp, assignment)
    scores_by_group = aggregate_assignment_scores_by_group(inp, assignment)

    table = Table(
        title="Assignment",
        # alternating background to separate rows
        row_styles=["", "on grey19"],
    )
    table.add_column("Group", style="bold")
    table.add_column("Course Type", style="grey50", header_style="grey50")
    table.add_column("Degree Type", style="grey50", header_style="grey50")
    table.add_column("Min Size", justify="right")
    table.add_column("Capacity", justify="right")
    table.add_column("# Students", justify="right", style="bold")
    table.add_column("%", justify="right")
    for score in scores_by_group:
        table.add_column(
            f"{score}", justify="right", style="grey50", header_style="grey50"
        )

    for group in inp.groups:
        count = students_by_group[group.id]
        band = group.capacity - group.min_size
        if group.capacity == 0:
            utilization = Text("")
        elif count > group.capacity:
            utilization = Text("> 100%", style="red")
        elif count < group.min_size:
            utilization = Text("< 0%", style="red")
        elif band == 0:
            utilization = Text("100%")
        else:
            utilization = Text(f"{(count - group.min_size) / band * 100:.0f}%")
        row: list[Text | str] = [
            group.name,
            group.course_type.value,
            group.degree_type.value,
            str(group.min_size),
            str(group.capacity),
            str(students_by_group[group.id]),
            utilization,
        ]
        row.extend(
            _fmt_score_count(score, scores_by_group[score][group.id])
            for score in scores_by_group
        )
        table.add_row(*row)

    return table


def build_same_type_assignment_table(
    inp: Input,
    assignment: Assignment,
    constraints: tuple[MinNumStudents, ...],
    tsa_only: bool,
) -> Table:
    width = 20
    students = "TSA students" if tsa_only else "Students"
    table = Table(
        title=f"# {students} by # students of their type in their group",
        # alternating background to separate rows
        row_styles=["", "on grey19"],
    )
    table.add_column("Types", style="bold")
    for i in range(1, width + 1):
        table.add_column(f"{i}", justify="right")
    table.add_column(f"≥{width + 1}", justify="right")

    def fmt(n: int) -> Text | str:
        return Text(str(n), style="red") if n > 0 else str(n)

    def type_parts(selector: StudentTypeSelector) -> tuple[str, str, str]:
        fluency = {None: "", True: "no german", False: "german"}
        return (
            selector.course_type.value if selector.course_type else "",
            selector.degree_type.value if selector.degree_type else "",
            fluency[selector.not_fluent_in_german],
        )

    for constraint in constraints:
        types = "\n".join(
            " ".join(part for part in parts if part)
            for parts in sorted(map(type_parts, constraint.types))
        )
        counts = count_students_by_type_count_in_groups(
            inp, assignment, constraint.types, tsa_only
        )
        row: list[Text | str] = [types]
        row.extend(fmt(counts.get(i, 0)) for i in range(1, width + 1))
        row.append(
            str(
                sum(
                    counts.get(i, 0)
                    for i in range(width + 1, max(counts.keys(), default=width) + 1)
                )
            )
        )
        table.add_row(*row)

    return table
