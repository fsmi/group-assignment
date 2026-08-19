from dataclasses import dataclass

from group_assignment.datatypes import TypeSelector


@dataclass(frozen=True)
class MinNumStudents:
    types: frozenset[TypeSelector]
    min: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.types:
            raise ValueError("MinNumStudents: types must contain at least one selector")
        if self.min < 0:
            raise ValueError(f"MinNumStudents: min must be >= 0 (got {self.min})")


@dataclass(frozen=True)
class Config:
    cost_base: int
    non_tsa_students_factor: float
    min_num_students: tuple[MinNumStudents, ...]
    min_size_factor: float
    capacity_factor: float

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.cost_base < 1:
            raise ValueError(f"Config: cost_base must be >= 1 (got {self.cost_base})")
        if self.non_tsa_students_factor < 1:
            raise ValueError(
                f"Config: non_tsa_students_factor must be >= 1 "
                f"(got {self.non_tsa_students_factor})"
            )
        if self.min_size_factor < 0:
            raise ValueError(
                f"Config: min_size_factor must be >= 0 (got {self.min_size_factor})"
            )
        if self.capacity_factor <= 0:
            raise ValueError(
                f"Config: capacity_factor must be > 0 (got {self.capacity_factor})"
            )
