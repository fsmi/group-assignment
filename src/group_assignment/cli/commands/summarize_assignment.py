import logging
from pathlib import Path

import click

from group_assignment.cli.utils import configure_logging
from group_assignment.io import parse_input_file, parse_output_file, validate_output
from group_assignment.model import Assignment, Input
from group_assignment.stats import (
    print_assignment_summary,
    print_group_assignment_summary,
)

logger = logging.getLogger(__name__)


@click.command(name="summarize-assignment")
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Input file.",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Assignment to summarize.",
)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    help="Show detailed per-group summaries.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def summarize_assignment(
    input_path: Path,
    output_path: Path,
    detailed: bool,
    verbose: bool,
) -> None:
    configure_logging(verbose)

    input_schema = parse_input_file(input_path)
    output_schema = parse_output_file(output_path)
    validate_output(input_schema, output_schema)

    inp = Input.build_from_input_schema(input_schema)
    ass = Assignment.build_from_output_schema(output_schema, inp)

    print_assignment_summary(inp, ass)
    if detailed:
        print_group_assignment_summary(inp, ass)
