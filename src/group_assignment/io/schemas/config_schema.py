from pydantic import BaseModel, ConfigDict, Field

from group_assignment.cp import Config
from group_assignment.cp.config import GroupSize, MinDegreeTypeShare, MinNumStudents
from group_assignment.datatypes import DegreeType, StudentTypeSelector


class CostSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base: int = Field(gt=1)
    non_tsa_students_factor: float = Field(gt=1)


class MinNumStudentsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    types: frozenset[StudentTypeSelector] = Field(min_length=1)
    min: int = Field(ge=0)

    def to_config(self) -> MinNumStudents:
        return MinNumStudents(types=self.types, min=self.min)


class MinDegreeTypeShareSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree_type: DegreeType
    min: float = Field(ge=0, le=1)

    def to_config(self) -> MinDegreeTypeShare:
        return MinDegreeTypeShare(degree_type=self.degree_type, min=self.min)


class GroupSizeSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_factor: float = Field(ge=0)
    min_size: int = Field(ge=0)
    min_capacity_factor: float = Field(ge=0)
    capacity_factor: float = Field(gt=0)

    def to_config(self) -> GroupSize:
        return GroupSize(
            min_factor=self.min_factor,
            min_size=self.min_size,
            min_capacity_factor=self.min_capacity_factor,
            capacity_factor=self.capacity_factor,
        )


class ConstraintsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_num_students_tsa: list[MinNumStudentsSchema]
    min_num_students_all: list[MinNumStudentsSchema]
    min_degree_type_shares: list[MinDegreeTypeShareSchema]
    group_size: GroupSizeSchema


class ConfigSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost: CostSchema
    constraints: ConstraintsSchema

    def to_config(self) -> Config:
        return Config(
            cost_base=self.cost.base,
            non_tsa_students_factor=self.cost.non_tsa_students_factor,
            min_num_students_tsa=tuple(
                e.to_config() for e in self.constraints.min_num_students_tsa
            ),
            min_num_students_all=tuple(
                e.to_config() for e in self.constraints.min_num_students_all
            ),
            min_degree_type_shares=tuple(
                e.to_config() for e in self.constraints.min_degree_type_shares
            ),
            group_size=self.constraints.group_size.to_config(),
        )
