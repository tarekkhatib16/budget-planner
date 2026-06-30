"""Savings arithmetic for the yearly view.

Monthly savings = income - bills - spending - actual unusual expenses.

Income/bills/spending are budgeted (planned) amounts. Unusual expenses are
*actuals* — what you really spent on one-off costs like holidays, summed
per month. DEBT rows are reference balances and never enter this sum.
"""

from itertools import accumulate

from api.shared.enums import CategoryGroup

MONTHS_IN_YEAR = 12

# Groups whose budgeted totals reduce savings each month.
OUTGOING_GROUPS = (CategoryGroup.BILLS, CategoryGroup.SPENDING)


def monthly_savings(
    group_totals: dict[CategoryGroup, list[int]],
    monthly_unusual_pence: list[int],
) -> list[int]:
    """Per-month savings from per-group monthly totals and actual unusual spend."""
    income = group_totals.get(CategoryGroup.INCOME, [0] * MONTHS_IN_YEAR)
    savings = list(income)
    for group in OUTGOING_GROUPS:
        for i, amount in enumerate(group_totals.get(group, [0] * MONTHS_IN_YEAR)):
            savings[i] -= amount
    for i, amount in enumerate(monthly_unusual_pence):
        savings[i] -= amount
    return savings


def cumulative_savings(savings: list[int]) -> list[int]:
    return list(accumulate(savings))
