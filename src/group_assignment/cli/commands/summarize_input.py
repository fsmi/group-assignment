import logging
from pathlib import Path

import click

from group_assignment.cli.utils import configure_logging
from group_assignment.io import parse_input_file
from group_assignment.model import Input
from group_assignment.stats import print_input_summary

logger = logging.getLogger(__name__)


@click.command(name="summarize-input")
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Input file to summarize.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def summarize_input(input_path: Path, verbose: bool) -> None:
    configure_logging(verbose)

    input_schema = parse_input_file(input_path)
    inp = Input.build_from_input_schema(input_schema)
    print_input_summary(inp)
