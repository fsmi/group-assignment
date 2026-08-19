from pydantic import BaseModel, ConfigDict, Field

from group_assignment.cp import Config, MinNumStudents
from group_assignment.datatypes import TypeSelector


class Cost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base: int = Field(gt=1)
    non_tsa_students_factor: float = Field(gt=1)


class MinNumStudentsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    types: frozenset[TypeSelector] = Field(min_length=1)
    min: int = Field(ge=0)

    def to_min_num_students(self) -> MinNumStudents:
        return MinNumStudents(types=self.types, min=self.min)


class Constraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_num_students: list[MinNumStudentsSchema]
    min_size_factor: float = Field(ge=0)
    capacity_factor: float = Field(ge=0)


class ConfigSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cost: Cost
    constraints: Constraints

    def to_config(self) -> Config:
        return Config(
            cost_base=self.cost.base,
            non_tsa_students_factor=self.cost.non_tsa_students_factor,
            min_num_students=tuple(
                e.to_min_num_students() for e in self.constraints.min_num_students
            ),
            min_size_factor=self.constraints.min_size_factor,
            capacity_factor=self.constraints.capacity_factor,
        )
