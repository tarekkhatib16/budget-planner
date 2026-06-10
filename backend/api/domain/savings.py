"""Savings arithmetic for the yearly view.

Monthly savings = income - bills - spending - holiday, exactly as in the
spreadsheet. DEBT rows are reference balances and never enter this sum.
"""

from itertools import accumulate

from api.shared.enums import CategoryGroup

MONTHS_IN_YEAR = 12

# Groups that reduce savings each month.
OUTGOING_GROUPS = (CategoryGroup.BILLS, CategoryGroup.SPENDING, CategoryGroup.HOLIDAY)


def monthly_savings(group_totals: dict[CategoryGroup, list[int]]) -> list[int]:
    """Per-month savings from per-group monthly totals (12 values each)."""
    income = group_totals.get(CategoryGroup.INCOME, [0] * MONTHS_IN_YEAR)
    savings = list(income)
    for group in OUTGOING_GROUPS:
        for i, amount in enumerate(group_totals.get(group, [0] * MONTHS_IN_YEAR)):
            savings[i] -= amount
    return savings


def cumulative_savings(savings: list[int]) -> list[int]:
    return list(accumulate(savings))
