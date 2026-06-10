from enum import Enum


class CategoryGroup(str, Enum):
    """Section of the yearly budget grid a category belongs to.

    INCOME, BILLS, SPENDING and HOLIDAY feed the monthly savings calculation
    (income - bills - spending - holiday). DEBT rows are tracked balances
    (e.g. credit card debt) shown for reference and excluded from savings.
    SPENDING is the group whose monthly total is divided across the weeks of
    the month in the weekly tracker.
    """

    INCOME = "income"
    BILLS = "bills"
    SPENDING = "spending"
    HOLIDAY = "holiday"
    DEBT = "debt"
