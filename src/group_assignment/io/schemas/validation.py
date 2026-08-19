import logging

from .input_schema import InputSchema
from .output_schema import OutputSchema

logger = logging.getLogger(__name__)


def validate_output(i: InputSchema, o: OutputSchema) -> None:
    logger.info("Validating OutputSchema against InputSchema")

    # validate that each team is assigned to a group
    teams_not_assigned = set(i.teams.keys()) - set(o.root.keys())
    if teams_not_assigned:
        logger.error(f"Teams {teams_not_assigned} not assigned to any group")

    # validate that only known teams are assigned
    unknown_teams = set(o.root.keys()) - set(i.teams.keys())
    if unknown_teams:
        unknown_team = unknown_teams.pop()
        raise ValueError(f"Assignment for unknown Team {unknown_team}")

    # validate that all groups are known
    for tid, gid in o.root.items():
        if gid not in i.groups:
            raise ValueError(f"Team {tid} assigned to unknown group {gid}")
