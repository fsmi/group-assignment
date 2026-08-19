from pathlib import Path

import click

from group_assignment.cli.utils import configure_logging
from group_assignment.cp import CP
from group_assignment.io import (
    parse_config_file,
    parse_input_file,
    validate_output,
    write_output_file,
)
from group_assignment.model import Assignment, Input
from group_assignment.stats import (
    print_assignment_summary,
    print_group_assignment_summary,
)


@click.command()
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
    type=click.Path(dir_okay=False, path_type=Path),
    required=True,
    help="Path to write assignment to.",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Config file to use.",
)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    help="Show detailed per-group summaries.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def assign(
    input_path: Path,
    output_path: Path,
    config_path: Path,
    detailed: bool,
    verbose: bool,
) -> None:
    configure_logging(verbose)

    input_schema = parse_input_file(input_path)
    inp = Input.build_from_input_schema(input_schema)

    config_schema = parse_config_file(config_path)
    config = config_schema.to_config()

    ass_id_mapping = CP.build_from_input(inp, config).solve()

    ass = Assignment.build_from_id_mapping(ass_id_mapping, inp)
    output_schema = ass.to_output_schema()
    validate_output(input_schema, output_schema)
    write_output_file(output_path, output_schema)

    print_assignment_summary(inp, ass)
    if detailed:
        print_group_assignment_summary(inp, ass)
