import rich
from rich.align import Align
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from group_assignment.model import Input

from .input_stats import (
    aggregate_ratings_by_groups,
    count_students_by_type,
    sum_group_capacities,
    sum_group_min_sizes,
)
from .utils import build_crosstable


def print_input_summary(data: Input) -> None:
    students_table = build_crosstable(
        count_students_by_type(data),
        "# Students",
        "Course/Degree",
    )
    groups_table = _build_groups_table(data)

    tables = Group(
        Align.center(Padding(students_table, (1, 0, 1, 0))), Align.center(groups_table)
    )
    panel = Panel(
        tables,
        title="Input",
        expand=False,
    )
    rich.print(panel)


def _build_groups_table(data: Input) -> Table:
    ratings = aggregate_ratings_by_groups(data)
    scores = sorted(ratings.keys())

    table = Table(title="Groups and Ratings")
    table.add_column("Group", style="bold")
    table.add_column("Course Type")
    table.add_column("Degree Type")
    table.add_column("Min Size", justify="right")
    table.add_column("Capacity", justify="right")
    for score in scores:
        table.add_column(f"{score}", justify="right")

    for group in data.groups:
        row: list[str | Text] = [
            group.name,
            group.course_type.value,
            group.degree_type.value,
            str(group.min_size),
            str(group.capacity),
        ]

        count_min_score = ratings[scores[0]][group.id]
        row.append(
            Text(
                str(count_min_score),
                style="red" if count_min_score < group.min_size else "",
            )
        )
        row.extend(str(ratings[score][group.id]) for score in scores[1:])
        table.add_row(*row)

    table.add_section()
    table.add_row(
        *([""] * 3),
        str(sum_group_min_sizes(data)),
        str(sum_group_capacities(data)),
        style="grey50 bold",
    )
    return table
