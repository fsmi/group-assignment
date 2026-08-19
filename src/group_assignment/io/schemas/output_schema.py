from pydantic import RootModel

from group_assignment.datatypes import GroupID, TeamID


class OutputSchema(RootModel[dict[TeamID, GroupID]]):
    pass
