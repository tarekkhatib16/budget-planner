from api.domain.savings import MONTHS_IN_YEAR, cumulative_savings, monthly_savings
from api.exceptions.errors import NotFoundError
from api.models import BudgetEntry
from api.repositories.budget_repository import BudgetRepository
from api.repositories.category_repository import CategoryRepository
from api.schemas.budget import CategoryRow, GroupSection, YearView
from api.shared.enums import CategoryGroup

# Display order of the grid sections, matching the spreadsheet layout.
GROUP_ORDER = (
    CategoryGroup.INCOME,
    CategoryGroup.BILLS,
    CategoryGroup.SPENDING,
    CategoryGroup.HOLIDAY,
    CategoryGroup.DEBT,
)


class BudgetService:
    def __init__(
        self, categories: CategoryRepository, budgets: BudgetRepository, user_id: int
    ) -> None:
        self._categories = categories
        self._budgets = budgets
        self._user_id = user_id

    def set_amount(
        self, category_id: int, year: int, month: int, amount_pence: int
    ) -> BudgetEntry:
        if self._categories.get(self._user_id, category_id) is None:
            raise NotFoundError(f"Category {category_id} not found")
        return self._budgets.upsert(self._user_id, category_id, year, month, amount_pence)

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

        savings = monthly_savings(group_totals)
        return YearView(
            year=year,
            sections=sections,
            monthly_savings_pence=savings,
            cumulative_savings_pence=cumulative_savings(savings),
        )
