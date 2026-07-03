"""Week arithmetic for the monthly tracker.

Weeks align to Monday–Sunday. The first week of the month runs from day 1
to the following Sunday (short when the month doesn't start on Monday);
subsequent weeks are full Mon–Sun; the last week is truncated at month end.

The monthly spending budget is spread across those weeks in proportion to
their length, so a partial first week gets a proportionally smaller share.

Pure functions only — no database or framework imports — so this is
trivially unit-testable.
"""

from dataclasses import dataclass
from datetime import date

from api.utils.dates import days_in_month

WEEK_LENGTH = 7
# Python's date.weekday() returns Monday=0 .. Sunday=6.
_SUNDAY = 6


@dataclass(frozen=True)
class Week:
    index: int  # 1-based, "Week 1" .. "Week 5" (or 6 if the month spans six)
    start: date
    end: date  # inclusive

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


def _first_week_length(first_day_of_week: int) -> int:
    """How many days from day 1 up to and including the first Sunday.

    Monday=0 → 7 (whole week), Wednesday=2 → 5, Sunday=6 → 1.
    """
    return WEEK_LENGTH - first_day_of_week


def weeks_of_month(year: int, month: int) -> list[Week]:
    total_days = days_in_month(year, month)
    first_dow = date(year, month, 1).weekday()
    weeks = []

    # Week 1 runs from day 1 to the following Sunday (or end of month).
    end_day = min(_first_week_length(first_dow), total_days)
    weeks.append(
        Week(index=1, start=date(year, month, 1), end=date(year, month, end_day))
    )

    # Subsequent full Mon–Sun weeks, last one truncated at month end.
    day = end_day + 1
    while day <= total_days:
        end_day = min(day + WEEK_LENGTH - 1, total_days)
        weeks.append(
            Week(
                index=len(weeks) + 1,
                start=date(year, month, day),
                end=date(year, month, end_day),
            )
        )
        day = end_day + 1
    return weeks


def allocate_allowances(total_pence: int, weeks: list[Week]) -> list[int]:
    """Split a monthly budget across weeks, pro rata by days.

    Allocates cumulative floor((total * days_so_far) / total_days) so the
    per-week amounts are whole pence and always sum exactly to the total.
    """
    total_days = sum(week.days for week in weeks)
    allowances = []
    days_so_far = 0
    allocated = 0
    for week in weeks:
        days_so_far += week.days
        cumulative = total_pence * days_so_far // total_days
        allowances.append(cumulative - allocated)
        allocated = cumulative
    return allowances


def week_index_for(day: date) -> int:
    """Which week of its month a date falls in (1-based).

    Computed directly rather than by scanning weeks_of_month(): first_week
    ends on the first Sunday, then every subsequent Mon–Sun block is one
    week.
    """
    first_dow = date(day.year, day.month, 1).weekday()
    first_week_length = _first_week_length(first_dow)
    if day.day <= first_week_length:
        return 1
    return 2 + (day.day - first_week_length - 1) // WEEK_LENGTH
