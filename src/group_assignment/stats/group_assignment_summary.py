import rich
from rich.columns import Columns
from rich.padding import Padding
from rich.panel import Panel

from group_assignment.model import Assignment, Input

from .assignment_stats import count_students_in_group_by_type
from .utils import build_crosstable


def print_group_assignment_summary(inp: Input, assignment: Assignment) -> None:
    tables: list[Padding] = []

    for group in inp.groups:
        stats = count_students_in_group_by_type(inp, assignment, group.id)
        tables.append(
            Padding(
                build_crosstable(
                    stats,
                    group.name,
                    "Course/Degree",
                ),
                (1, 0, 0, 0),
            )
        )

    rich.print(
        Panel(
            Columns(tables, expand=True, equal=True),
            title="# Students Assigned to Groups",
            expand=False,
        )
    )
