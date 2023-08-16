from __future__ import annotations

import hypothesis.strategies as st
import pytest
from hypothesis import given, settings


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


@pytest.mark.parametrize("year", [1600, 1700, 1800, 1900])
def test_that_years_divisible_by_100_are_not_leap_years_unless_divisible_by_400(year):
    if year % 100 == 0:
        assert not is_leap_year(year) or year % 400 == 0


@pytest.mark.parametrize("year", [1904, 1914, 1918, 1939, 1945, 1908, 2004])
def test_that_only_years_divisible_by_four_are_leap_years(year):
    if year % 4 != 0:
        assert not is_leap_year(year)
    if is_leap_year(year):
        assert year % 4 == 0


@pytest.mark.parametrize("year", [1900, 1908, 1914, 1918, 2004])
def test_that_years_divisible_by_4_and_not_by_100_are_leap_years(year):
    if year % 4 == 0 and year % 100 != 0:
        assert is_leap_year(year)


class Expression:
    def __init__(self, left: Expression, operator: BinaryOperator, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __call__(self, year):
        return self.operator.callable(self.left(year), self.right(year))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.left) + str(self.operator) + str(self.right)


class Constant(Expression):
    def __init__(self, constant: int):
        self.constant = constant

    def __call__(self, _):
        return self.constant

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.constant)


class BinaryOperator:
    def __init__(self, callable, symbol) -> None:
        self.callable = callable
        self.symbol = symbol

    def __call__(self, left, right) -> Expression:
        return Expression(left, self, right)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.symbol


and_op = BinaryOperator(lambda a, b: a and b, "and")
or_op = BinaryOperator(lambda a, b: a or b, "or")
eq_op = BinaryOperator(lambda a, b: a == b, "==")
neq_op = BinaryOperator(lambda a, b: a != b, "!=")
geq_op = BinaryOperator(lambda a, b: a >= b, ">=")
leq_op = BinaryOperator(lambda a, b: a <= b, "<=")
ge_op = BinaryOperator(lambda a, b: a > b, ">")
le_op = BinaryOperator(lambda a, b: a < b, "<")
plus = BinaryOperator(lambda a, b: a + b, "+")
minus = BinaryOperator(lambda a, b: a - b, "-")
mod = BinaryOperator(lambda a, b: a % b, "%")

years = st.integers(min_value=1, max_value=10000)
constants = st.builds(Constant, years)
boolean_operators = st.sampled_from([and_op, or_op])
comparisons = st.sampled_from([eq_op, neq_op, geq_op, leq_op, ge_op, le_op])
integer_operators = st.sampled_from([plus, minus, mod])

is_divisible_candidates = comparisons.flatmap(
    lambda x: st.builds(
        x,
        integer_operators.flatmap(lambda x: st.builds(x, constants, constants)),
        constants,
    ),
)

is_leap_year_candidates = boolean_operators.flatmap(
    lambda x: st.builds(
        x,
        boolean_operators.flatmap(
            lambda x: st.builds(x, is_divisible_candidates, is_divisible_candidates)
        ),
        is_divisible_candidates,
    )
)


@settings(max_examples=1000000)
@given(is_leap_year_candidates)
def test_that_no_mutants_exist(is_leap_year_mutant):
    assert (
        any(
            year % 100 == 0 and is_leap_year_mutant(year) and year % 400 == 0
            for year in [1600, 1700, 1800, 1900]
        )
        or any(
            (year % 4 != 0 and is_leap_year_mutant(year))
            or (is_leap_year_mutant(year) and year % 4 != 0)
            for year in [1904, 1914, 1918, 1939, 1945, 1908, 2004]
        )
        or any(
            (year % 4 == 0 and year % 100 != 0 and not is_leap_year_mutant(year))
            or (is_leap_year_mutant(year) and year % 4 != 0)
            for year in [1900, 1908, 1914, 1918, 2004]
        )
    )
