from enum import Enum


class CategoryGroup(str, Enum):
    """Section of the yearly budget grid a category belongs to.

    INCOME, BILLS, and SPENDING feed the monthly savings calculation
    (income - bills - spending - actual unusual expenses). DEBT rows are
    tracked balances (e.g. credit card debt) shown for reference and
    excluded from savings. SPENDING is the group whose monthly total is
    divided across the weeks of the month in the weekly tracker.

    HOLIDAY is preserved on the enum so old data can still be read, but the
    application no longer seeds, displays, or planning-budgets it — unusual
    expenses are now tracked actuals (see ExpenseKind.UNUSUAL) rather than
    budgeted plans.
    """

    INCOME = "income"
    BILLS = "bills"
    SPENDING = "spending"
    HOLIDAY = "holiday"  # legacy, no longer used
    DEBT = "debt"  # legacy, no longer used


class ExpenseKind(str, Enum):
    """How a logged expense feeds the views.

    REGULAR expenses count against the month's SPENDING budget and show in
    the weekly tracker. UNUSUAL expenses are one-off costs (holidays, big
    purchases) tracked as actuals — they reduce monthly savings but aren't
    budgeted in advance.
    """

    REGULAR = "regular"
    UNUSUAL = "unusual"
