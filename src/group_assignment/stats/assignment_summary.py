import rich
from rich.align import Align
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from group_assignment.cp import Config
from group_assignment.cp.config import MinNumStudents
from group_assignment.datatypes import TypeSelector
from group_assignment.model import Assignment, Input, Student

from .assignment_stats import (
    aggregate_assignment_scores,
    aggregate_assignment_scores_by_group,
    count_students_by_group,
    count_students_by_type_count_in_groups,
)


def print_assignment_summary(
    inp: Input, assignment: Assignment, config: Config | None = None
) -> None:
    tables = [
        build_acc_scores_table(inp, assignment),
        build_group_stats_table(inp, assignment),
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
    scores_tsa_false = aggregate_assignment_scores(
        inp, assignment, Student.Selector(type_specific_assignment=False)
    )
    scores_tsa_true = aggregate_assignment_scores(
        inp, assignment, Student.Selector(type_specific_assignment=True)
    )

    table = Table(title="Scores")
    table.add_column("Score", style="bold", justify="right")
    table.add_column("# Students", justify="right")
    table.add_column(
        "tsa=False",
        justify="right",
        style="grey50",
        header_style="grey50",
    )
    table.add_column(
        "tsa=True",
        justify="right",
        style="grey50",
        header_style="grey50",
    )

    for score in scores:
        table.add_row(
            f"{score}",
            str(scores[score]),
            str(scores_tsa_false[score]),
            str(scores_tsa_true[score]),
        )

    return table


def build_group_stats_table(inp: Input, assignment: Assignment) -> Table:
    students_by_group = count_students_by_group(inp, assignment)
    scores_by_group = aggregate_assignment_scores_by_group(inp, assignment)

    table = Table(title="Assignment")
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
        row.extend(str(scores_by_group[score][group.id]) for score in scores_by_group)
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

    def type_parts(selector: TypeSelector) -> tuple[str, str]:
        return (
            selector.course_type.value if selector.course_type else "",
            selector.degree_type.value if selector.degree_type else "",
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
