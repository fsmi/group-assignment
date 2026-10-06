from __future__ import annotations

import logging
import math
import time
from collections.abc import Mapping
from typing import Self

from ortools.sat.python import cp_model

from group_assignment.datatypes import GroupID, TeamID
from group_assignment.model import Input, Student

from .config import Config

logger = logging.getLogger(__name__)


class CP:
    _model: cp_model.CpModel
    _x: dict[tuple[TeamID, GroupID], cp_model.IntVar]

    def __init__(
        self,
        model: cp_model.CpModel,
        x: dict[tuple[TeamID, GroupID], cp_model.IntVar],
    ) -> None:
        self._model = model
        self._x = x

    @classmethod
    def build_from_input(cls, inp: Input, config: Config) -> Self:
        logger.info("Building CP model from Input")
        model = cp_model.CpModel()

        # ==== VARIABLES ====

        # x[(tid, gid)] = 1 if team with id tid is assigned to group with id gid
        x = {
            (t.id, g.id): model.new_bool_var(f"x[({t.id},{g.id})]")
            for t in inp.teams
            for g in t.rating
        }

        # ==== CONSTRAINTS ====

        # each team assigned to exactly one group
        for t in inp.teams:
            model.add(sum(x[(t.id, g.id)] for g in t.rating) == 1)

        # group capacity and minimum size
        for g in inp.groups:
            group_size = sum(
                t.size * x[(t.id, g.id)] for t in inp.teams if g in t.rating
            )
            model.add(
                group_size <= math.floor(g.capacity * config.group_size.capacity_factor)
            )
            min_size = max(
                math.ceil(g.min_size * config.group_size.min_factor),
                config.group_size.min_size,
                math.ceil(g.capacity * config.group_size.min_capacity_factor),
            )
            model.add(group_size >= min_size)

        # minimum number of students of each set of types in each group
        for constraint in config.min_num_students:
            tsa_selectors = frozenset(
                Student.Selector.from_type_selector(
                    selector, type_specific_assignment=True
                )
                for selector in constraint.types
            )

            for g in inp.groups:
                count_of_types = sum(
                    x[(t.id, g.id)] * t.num_students(constraint.types)
                    for t in inp.teams
                    if g in t.rating
                )
                count_of_tsa_students_of_types = sum(
                    x[(t.id, g.id)] * t.num_students(tsa_selectors)
                    for t in inp.teams
                    if g in t.rating
                )

                has_tsa_students_of_types = model.new_bool_var(
                    f"has_tsa_students_of_types[({g.id},{constraint.types})]"
                )
                model.add(count_of_tsa_students_of_types > 0).OnlyEnforceIf(
                    has_tsa_students_of_types
                )
                model.add(count_of_tsa_students_of_types <= 0).OnlyEnforceIf(
                    has_tsa_students_of_types.Not()
                )

                model.add(count_of_types >= constraint.min).OnlyEnforceIf(
                    has_tsa_students_of_types
                )

        # ==== OBJECTIVE ====

        model.minimize(
            sum(
                x[(t.id, g.id)]
                * (
                    (config.cost_base ** t.rating[g] - 1)
                    * (
                        config.non_tsa_students_factor
                        * t.num_students(
                            Student.Selector(type_specific_assignment=False)
                        )
                        + t.num_students(
                            Student.Selector(type_specific_assignment=True)
                        )
                    )
                )
                for t in inp.teams
                for g in t.rating
            )
        )

        return cls(model, x)

    def solve(self) -> Mapping[TeamID, GroupID]:
        logger.info("Solving CP")

        solver = cp_model.CpSolver()
        # deterministic behavior
        solver.parameters.random_seed = 42

        start_time = time.time()
        status = solver.solve(self._model)
        end_time = time.time()

        elapsed_time = end_time - start_time
        logger.info(
            f"Solver status: {solver.status_name(status)}, "
            f"Solver value: {solver.objective_value}, "
            f"Time elapsed: {elapsed_time:.4f}s"
        )
        if solver.status_name(status) not in {
            "OPTIMAL",
            "FEASIBLE",
        }:
            raise RuntimeError("No feasible solution found")

        return self._get_assignment(solver)

    def _get_assignment(self, solver: cp_model.CpSolver) -> Mapping[TeamID, GroupID]:
        assignment: dict[TeamID, GroupID] = {}
        for (tid, gid), var in self._x.items():
            if solver.value(var) == 1:
                assignment[tid] = gid
        return assignment
