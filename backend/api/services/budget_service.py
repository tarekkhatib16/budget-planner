from api.domain.savings import MONTHS_IN_YEAR, cumulative_savings, monthly_savings
from api.exceptions.errors import NotFoundError
from api.models import BudgetEntry
from api.repositories.budget_repository import BudgetRepository
from api.repositories.category_repository import CategoryRepository
from api.repositories.expense_repository import ExpenseRepository
from api.schemas.budget import CategoryRow, GroupSection, YearView
from api.shared.enums import CategoryGroup, ExpenseKind

# Display order of the editable budget sections. HOLIDAY and DEBT are
# legacy: holidays are now actuals surfaced via monthly_unusual_pence,
# and debt is no longer tracked here.
GROUP_ORDER = (
    CategoryGroup.INCOME,
    CategoryGroup.BILLS,
    CategoryGroup.SPENDING,
)


class BudgetService:
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

    def set_amount(
        self, category_id: int, year: int, month: int, amount_pence: int
    ) -> BudgetEntry:
        if self._categories.get(self._user_id, category_id) is None:
            raise NotFoundError(f"Category {category_id} not found")
        return self._budgets.upsert(self._user_id, category_id, year, month, amount_pence)

    def copy_forward(self, year: int, month: int) -> int:
        """Make every later month of `year` identical to `month`.

        Categories with no amount in the source month are set to zero in the
        future months too, so the result is a true copy, not a merge.
        Returns how many months were filled.
        """
        categories = self._categories.list_all(self._user_id)
        amounts = {
            entry.category_id: entry.amount_pence
            for entry in self._budgets.list_for_month(self._user_id, year, month)
        }
        future_months = range(month + 1, MONTHS_IN_YEAR + 1)
        for future_month in future_months:
            for category in categories:
                self._budgets.upsert(
                    self._user_id, category.id, year, future_month, amounts.get(category.id, 0)
                )
        return len(future_months)

    def get_year_view(self, year: int) -> YearView:
        categories = self._categories.list_all(self._user_id)
        amounts = {
            (entry.category_id, entry.month): entry.amount_pence
            for entry in self._budgets.list_for_year(self._user_id, year)
        }

        sections = []
        group_totals: dict[CategoryGroup, list[int]] = {}
        for group in GROUP_ORDER:
            rows = [
                CategoryRow(
                    category_id=category.id,
                    name=category.name,
                    amounts_pence=[
                        amounts.get((category.id, month), 0)
                        for month in range(1, MONTHS_IN_YEAR + 1)
                    ],
                )
                for category in categories
                if category.group == group
            ]
            totals = [
                sum(row.amounts_pence[i] for row in rows) for i in range(MONTHS_IN_YEAR)
            ]
            group_totals[group] = totals
            sections.append(GroupSection(group=group, rows=rows, totals_pence=totals))

        unusual_by_month = self._expenses.monthly_totals(
            self._user_id, year, ExpenseKind.UNUSUAL
        )
        monthly_unusual = [
            unusual_by_month.get(month, 0) for month in range(1, MONTHS_IN_YEAR + 1)
        ]

        savings = monthly_savings(group_totals, monthly_unusual)
        return YearView(
            year=year,
            sections=sections,
            monthly_unusual_pence=monthly_unusual,
            monthly_savings_pence=savings,
            cumulative_savings_pence=cumulative_savings(savings),
        )
