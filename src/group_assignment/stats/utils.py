from typing import Any

import rich
import rich.box
from rich.table import Table


def build_crosstable(
    data: dict[tuple[Any, Any], int], title: str = "", corner_label: str = ""
) -> Table:
    rows = list(dict.fromkeys(row for row, _ in data))
    cols = list(dict.fromkeys(col for _, col in data))

    table = Table(title=title, box=rich.box.SQUARE)

    table.add_column(f"[italic]{corner_label}[/italic]", style="bold")
    for col in cols:
        table.add_column(str(col), justify="right")
    table.add_column(justify="right", style="bold italic grey50")

    for row in rows:
        row_data = [str(row)]
        row_data.extend(str(data[(row, col)]) for col in cols)
        row_data.append(str(sum(data[(row, col)] for col in cols)))
        table.add_row(*row_data, end_section=True)

    row = [""]
    for col in cols:
        row.append(str(sum(data[(row, col)] for row in rows)))
    row.append(f"[underline]{sum(data.values())!s}[/underline]")
    table.add_row(*row, style="bold italic grey50")

    return table
