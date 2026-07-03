from datetime import date

from api.domain.weeks import allocate_allowances, week_index_for, weeks_of_month


def test_month_starting_monday_has_four_full_weeks_and_short_tail():
    # 1 Jun 2026 is a Monday, so weeks align cleanly Mon–Sun.
    weeks = weeks_of_month(2026, 6)
    assert [w.days for w in weeks] == [7, 7, 7, 7, 2]
    assert weeks[0].start == date(2026, 6, 1)
    assert weeks[0].start.weekday() == 0  # Monday
    assert weeks[-1].end == date(2026, 6, 30)


def test_month_starting_wednesday_has_short_first_week_ending_sunday():
    # 1 Jul 2026 is a Wednesday. Week 1 should be Wed–Sun (5 days), then
    # full Mon–Sun weeks, then a short tail.
    weeks = weeks_of_month(2026, 7)
    assert [w.days for w in weeks] == [5, 7, 7, 7, 5]
    assert weeks[0].start == date(2026, 7, 1)
    assert weeks[0].end == date(2026, 7, 5)  # Sunday
    assert weeks[1].start == date(2026, 7, 6)  # Monday
    assert weeks[1].start.weekday() == 0


def test_month_starting_sunday_has_one_day_first_week():
    # 1 Feb 2026 is a Sunday. Week 1 is just that one day.
    weeks = weeks_of_month(2026, 2)
    assert [w.days for w in weeks] == [1, 7, 7, 7, 6]
    assert weeks[0].end == date(2026, 2, 1)
    assert weeks[1].start == date(2026, 2, 2)  # Monday
    assert weeks[1].start.weekday() == 0


def test_allowances_are_pro_rata_and_sum_to_total():
    weeks = weeks_of_month(2026, 6)
    allowances = allocate_allowances(80_000, weeks)  # £800.00
    assert sum(allowances) == 80_000
    # 30 days total. Full weeks (7 days) get 7/30 * 80000 ≈ 18_666,
    # the 2-day tail gets proportionally less.
    assert allowances[0] == 18_666
    assert allowances[-1] < allowances[0] // 2


def test_short_first_week_gets_proportionally_smaller_allowance():
    # Jul 2026: Wed–Sun opener should get 5/31 of the budget.
    weeks = weeks_of_month(2026, 7)
    allowances = allocate_allowances(100_000, weeks)  # £1000
    assert sum(allowances) == 100_000
    # A 5-day week gets ~5/31, a 7-day week gets ~7/31, so the opener is
    # noticeably smaller than the second week.
    assert allowances[0] < allowances[1]


def test_zero_budget_allocates_zero():
    assert allocate_allowances(0, weeks_of_month(2026, 6)) == [0, 0, 0, 0, 0]


def test_week_index_buckets_by_calendar_week_for_monday_start_month():
    # June 2026 starts on Monday, so day 1..7 = week 1, 8..14 = week 2, etc.
    assert week_index_for(date(2026, 6, 1)) == 1
    assert week_index_for(date(2026, 6, 7)) == 1
    assert week_index_for(date(2026, 6, 8)) == 2
    assert week_index_for(date(2026, 6, 30)) == 5


def test_week_index_respects_short_first_week_for_mid_week_start():
    # July 2026 starts on Wednesday. Week 1 = Wed 1 .. Sun 5,
    # Week 2 = Mon 6 .. Sun 12, and so on.
    assert week_index_for(date(2026, 7, 1)) == 1  # Wed
    assert week_index_for(date(2026, 7, 5)) == 1  # Sun (end of week 1)
    assert week_index_for(date(2026, 7, 6)) == 2  # Mon (start of week 2)
    assert week_index_for(date(2026, 7, 12)) == 2
    assert week_index_for(date(2026, 7, 13)) == 3
    assert week_index_for(date(2026, 7, 27)) == 5  # Mon (start of last week)
    assert week_index_for(date(2026, 7, 31)) == 5  # Fri (end of month)
