from api.domain.weeks import allocate_allowances, week_index_for, weeks_of_month
from api.repositories.budget_repository import BudgetRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.expense_repository import ExpenseRepository
from api.schemas.expense import ExpenseRead
from api.schemas.month import MonthSummary, WeekSummary
from api.shared.enums import CategoryGroup, ExpenseKind
from api.utils.dates import month_bounds


class MonthService:
    """Builds the weekly tracker view: the month's SPENDING budget spread
    across its weeks, with REGULAR expenses bucketed into each week. Unusual
    expenses are excluded — they have their own view."""

    def __init__(
        self,
        categories: CategoryRepository,
        budgets: BudgetRepository,
        expenses: ExpenseRepository,
        user_id: int,
    ) -> None:
        self._categories = categories
        self._budgets = budgets
        self._expenses = expenses
        self._user_id = user_id

    def get_summary(self, year: int, month: int) -> MonthSummary:
        spending_ids = {
            c.id
            for c in self._categories.list_all(self._user_id)
            if c.group == CategoryGroup.SPENDING
        }
        budget = sum(
            entry.amount_pence
            for entry in self._budgets.list_for_month(self._user_id, year, month)
            if entry.category_id in spending_ids
        )

        weeks = weeks_of_month(year, month)
        allowances = allocate_allowances(budget, weeks)

        expenses_by_week: dict[int, list] = {week.index: [] for week in weeks}
        for expense in self._expenses.list_between(
            self._user_id, *month_bounds(year, month), kind=ExpenseKind.REGULAR
        ):
            expenses_by_week[week_index_for(expense.spend_date)].append(expense)

        week_summaries = []
        for week, allowance in zip(weeks, allowances):
            spent = sum(e.amount_pence for e in expenses_by_week[week.index])
            week_summaries.append(
                WeekSummary(
                    index=week.index,
                    start=week.start,
                    end=week.end,
                    allowance_pence=allowance,
                    spent_pence=spent,
                    saved_pence=allowance - spent,
                    expenses=[
                        ExpenseRead.model_validate(e) for e in expenses_by_week[week.index]
                    ],
                )
            )

        total_spent = sum(w.spent_pence for w in week_summaries)
        return MonthSummary(
            year=year,
            month=month,
            spending_budget_pence=budget,
            total_spent_pence=total_spent,
            total_saved_pence=budget - total_spent,
            weeks=week_summaries,
        )
