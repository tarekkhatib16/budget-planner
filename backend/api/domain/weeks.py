"""Week arithmetic for the monthly tracker.

A month is split into "weeks" of 7 days starting on the 1st (so the last
week is short: June has weeks of 7, 7, 7, 7 and 2 days). The monthly
spending budget is spread across those weeks in proportion to their length.

Pure functions only — no database or framework imports — so this is
trivially unit-testable.
"""

from dataclasses import dataclass
from datetime import date

from api.utils.dates import days_in_month

WEEK_LENGTH = 7


@dataclass(frozen=True)
class Week:
    index: int  # 1-based, "Week 1" .. "Week 5"
    start: date
    end: date  # inclusive

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


def weeks_of_month(year: int, month: int) -> list[Week]:
    total_days = days_in_month(year, month)
    weeks = []
    day = 1
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
    """Which week of its month a date falls in (1-based)."""
    return (day.day - 1) // WEEK_LENGTH + 1
