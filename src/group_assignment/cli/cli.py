import click

from .commands import assign, summarize_assignment, summarize_input


@click.group()
def cli() -> None:
    pass


cli.add_command(assign)
cli.add_command(summarize_input)
cli.add_command(summarize_assignment)
