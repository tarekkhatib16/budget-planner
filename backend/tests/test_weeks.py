from datetime import date

from api.domain.weeks import allocate_allowances, week_index_for, weeks_of_month


def test_june_has_five_weeks_with_short_tail():
    weeks = weeks_of_month(2026, 6)
    assert [w.days for w in weeks] == [7, 7, 7, 7, 2]
    assert weeks[0].start == date(2026, 6, 1)
    assert weeks[-1].end == date(2026, 6, 30)


def test_february_non_leap_has_exactly_four_weeks():
    weeks = weeks_of_month(2026, 2)
    assert [w.days for w in weeks] == [7, 7, 7, 7]


def test_allowances_are_pro_rata_and_sum_to_total():
    weeks = weeks_of_month(2026, 6)
    allowances = allocate_allowances(80_000, weeks)  # £800.00
    assert sum(allowances) == 80_000
    # Full weeks get ~7/30ths, the 2-day tail proportionally less.
    assert allowances[0] == 18_666
    assert allowances[-1] < allowances[0] // 2


def test_zero_budget_allocates_zero():
    assert allocate_allowances(0, weeks_of_month(2026, 6)) == [0, 0, 0, 0, 0]


def test_week_index_buckets_by_seven_days():
    assert week_index_for(date(2026, 6, 1)) == 1
    assert week_index_for(date(2026, 6, 7)) == 1
    assert week_index_for(date(2026, 6, 8)) == 2
    assert week_index_for(date(2026, 6, 30)) == 5
