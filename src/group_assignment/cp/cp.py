from __future__ import annotations

import itertools
import logging
import math
import time
from collections.abc import Collection, Mapping
from fractions import Fraction
from typing import Self

from ortools.sat.python import cp_model

from group_assignment.datatypes import GroupID, StudentTypeSelector, TeamID
from group_assignment.model import Input, Student

from .config import Config, MinNumStudents

logger = logging.getLogger(__name__)


class CP:
    _model: cp_model.CpModel
    _x: dict[tuple[TeamID, GroupID], cp_model.IntVar]
    _cost: cp_model.LinearExpr
    _fill_differences: list[tuple[cp_model.LinearExpr, int]] | None

    def __init__(
        self,
        model: cp_model.CpModel,
        x: dict[tuple[TeamID, GroupID], cp_model.IntVar],
        cost: cp_model.LinearExpr,
        fill_differences: list[tuple[cp_model.LinearExpr, int]] | None,
    ) -> None:
        self._model = model
        self._x = x
        self._cost = cost
        self._fill_differences = fill_differences

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

        def add_min_num_students(
            constraint: MinNumStudents,
            trigger_selectors: Collection[StudentTypeSelector | Student.Selector],
        ) -> None:
            # each group with students matching trigger_selectors needs at least
            # constraint.min students of constraint.types
            for g in inp.groups:
                count_of_types = sum(
                    x[(t.id, g.id)] * t.num_students(constraint.types)
                    for t in inp.teams
                    if g in t.rating
                )
                count_of_triggering_students = sum(
                    x[(t.id, g.id)] * t.num_students(trigger_selectors)
                    for t in inp.teams
                    if g in t.rating
                )

                is_triggered = model.new_bool_var(
                    f"is_triggered[({g.id},{constraint.types})]"
                )
                model.add(count_of_triggering_students > 0).OnlyEnforceIf(is_triggered)
                model.add(count_of_triggering_students <= 0).OnlyEnforceIf(
                    is_triggered.Not()
                )

                model.add(count_of_types >= constraint.min).OnlyEnforceIf(is_triggered)

        # minimum number of students of each set of types in each group with
        # TSA students of these types
        for constraint in config.min_num_students_tsa:
            tsa_selectors = frozenset(
                Student.Selector.from_type_selector(
                    selector, type_specific_assignment=True
                )
                for selector in constraint.types
            )
            add_min_num_students(constraint, tsa_selectors)

        # minimum number of students of each set of types in each group with
        # any students of these types
        for constraint in config.min_num_students_all:
            add_min_num_students(constraint, constraint.types)

        # minimum share of students of each degree type in each group that accepts
        # this degree type
        for constraint in config.min_degree_type_shares:
            min_share = Fraction(str(constraint.min))
            selector = StudentTypeSelector(degree_type=constraint.degree_type)
            for g in inp.groups:
                if not g.degree_type.accepts(constraint.degree_type):
                    continue
                group_size = sum(
                    t.size * x[(t.id, g.id)] for t in inp.teams if g in t.rating
                )
                count_of_degree_type = sum(
                    x[(t.id, g.id)] * t.num_students(selector)
                    for t in inp.teams
                    if g in t.rating
                )
                model.add(
                    min_share.denominator * count_of_degree_type
                    >= min_share.numerator * group_size
                )

        # ==== OBJECTIVES ====

        # primary: rating cost, scaled by the denominator of non_tsa_students_factor
        # so that all coefficients are integers (needed to fix it in phase 2 of
        # solve); minimized unscaled, so that the solver value is the actual cost
        non_tsa_factor = Fraction(str(config.non_tsa_students_factor))
        cost = cp_model.LinearExpr.weighted_sum(
            [x[(t.id, g.id)] for t in inp.teams for g in t.rating],
            [
                (config.cost_base ** t.rating[g] - 1)
                * (
                    non_tsa_factor.numerator
                    * t.num_students(Student.Selector(type_specific_assignment=False))
                    + non_tsa_factor.denominator
                    * t.num_students(Student.Selector(type_specific_assignment=True))
                )
                for t in inp.teams
                for g in t.rating
            ],
        )
        model.minimize(cost * (1 / non_tsa_factor.denominator))

        if not config.balance_group_sizes:
            return cls(model, x, cost, None)

        # secondary: pairwise differences of the fill ratios size/capacity,
        # cross-multiplied to stay integer:
        # c_h * s_g - c_g * s_h = c_g * c_h * (s_g/c_g - s_h/c_h),
        # each with an upper bound of its absolute value
        group_size = {
            g.id: cp_model.LinearExpr.weighted_sum(
                [x[(t.id, g.id)] for t in inp.teams if g in t.rating],
                [t.size for t in inp.teams if g in t.rating],
            )
            for g in inp.groups
        }
        max_group_size = {
            g.id: math.floor(g.capacity * config.group_size.capacity_factor)
            for g in inp.groups
        }
        fill_differences = [
            (
                h.capacity * group_size[g.id] - g.capacity * group_size[h.id],
                max(
                    h.capacity * max_group_size[g.id],
                    g.capacity * max_group_size[h.id],
                ),
            )
            for g, h in itertools.combinations(inp.groups, 2)
        ]

        return cls(model, x, cost, fill_differences)

    def solve(self) -> Mapping[TeamID, GroupID]:
        solver = cp_model.CpSolver()
        # deterministic behavior
        solver.parameters.random_seed = 42

        # phase 1: minimize the rating cost
        logger.info("Solving CP, phase 1: rating cost")
        self._solve(solver)
        if self._fill_differences is None:
            return self._get_assignment(solver)

        # phase 2: minimize the sum of absolute fill differences without worsening
        # the rating cost, starting from the phase 1 solution
        # (the absolute values are only added here, since they slow down phase 1)
        logger.info("Solving CP, phase 2: group size balance")
        self._model.add(self._cost <= solver.value(self._cost))
        for var in self._x.values():
            self._model.add_hint(var, solver.value(var))
        imbalances = []
        for diff, ub in self._fill_differences:
            imbalance = self._model.new_int_var(0, ub, "imbalance")
            self._model.add_abs_equality(imbalance, diff)
            imbalances.append(imbalance)
        self._model.minimize(cp_model.LinearExpr.sum(*imbalances))
        self._solve(solver)

        return self._get_assignment(solver)

    def _solve(self, solver: cp_model.CpSolver) -> None:
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

    def _get_assignment(self, solver: cp_model.CpSolver) -> Mapping[TeamID, GroupID]:
        assignment: dict[TeamID, GroupID] = {}
        for (tid, gid), var in self._x.items():
            if solver.value(var) == 1:
                assignment[tid] = gid
        return assignment
