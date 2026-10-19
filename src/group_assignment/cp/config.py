from dataclasses import dataclass

from group_assignment.datatypes import StudentTypeSelector


@dataclass(frozen=True)
class MinNumStudents:
    types: frozenset[StudentTypeSelector]
    min: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.types:
            raise ValueError("MinNumStudents: types must contain at least one selector")
        if self.min < 0:
            raise ValueError(f"MinNumStudents: min must be >= 0 (got {self.min})")


@dataclass(frozen=True)
class MinTypeShare:
    types: frozenset[StudentTypeSelector]
    min: float

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.types:
            raise ValueError("MinTypeShare: types must contain at least one selector")
        if not 0 <= self.min <= 1:
            raise ValueError(f"MinTypeShare: min must be in [0, 1] (got {self.min})")


@dataclass(frozen=True)
class GroupSize:
    min_factor: float
    min_size: int
    min_capacity_factor: float
    capacity_factor: float

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.min_factor < 0:
            raise ValueError(
                f"GroupSize: min_factor must be >= 0 (got {self.min_factor})"
            )
        if self.min_size < 0:
            raise ValueError(f"GroupSize: min_size must be >= 0 (got {self.min_size})")
        if self.min_capacity_factor < 0:
            raise ValueError(
                f"GroupSize: min_capacity_factor must be >= 0 "
                f"(got {self.min_capacity_factor})"
            )
        if self.capacity_factor <= 0:
            raise ValueError(
                f"GroupSize: capacity_factor must be > 0 (got {self.capacity_factor})"
            )


@dataclass(frozen=True)
class Config:
    cost_base: int
    non_tsa_students_factor: float
    balance_group_sizes: bool
    min_num_students_tsa: tuple[MinNumStudents, ...]
    min_num_students_all: tuple[MinNumStudents, ...]
    min_type_shares: tuple[MinTypeShare, ...]
    group_size: GroupSize

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.cost_base <= 1:
            raise ValueError(f"Config: cost_base must be > 1 (got {self.cost_base})")
        if self.non_tsa_students_factor < 1:
            raise ValueError(
                f"Config: non_tsa_students_factor must be >= 1 "
                f"(got {self.non_tsa_students_factor})"
            )
