import calendar
from datetime import date


def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def month_bounds(year: int, month: int) -> tuple[date, date]:
    """First and last day of the given month, inclusive."""
    return date(year, month, 1), date(year, month, days_in_month(year, month))
