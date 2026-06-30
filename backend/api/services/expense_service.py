from api.exceptions.errors import AppError, NotFoundError
from api.models import Expense
from api.repositories.category_repository import CategoryRepository
from api.repositories.expense_repository import ExpenseRepository
from api.schemas.expense import ExpenseCreate
from api.shared.enums import CategoryGroup, ExpenseKind
from api.utils.dates import month_bounds


class ExpenseService:
    def __init__(
        self,
        expenses: ExpenseRepository,
        categories: CategoryRepository,
        user_id: int,
    ) -> None:
        self._expenses = expenses
        self._categories = categories
        self._user_id = user_id

    def list_for_month(
        self, year: int, month: int, kind: ExpenseKind = ExpenseKind.REGULAR
    ) -> list[Expense]:
        return self._expenses.list_between(
            self._user_id, *month_bounds(year, month), kind=kind
        )

    def create(self, data: ExpenseCreate) -> Expense:
        if data.category_id is not None:
            category = self._categories.get(self._user_id, data.category_id)
            if category is None:
                raise NotFoundError(f"Category {data.category_id} not found")
            # Only Spending categories make sense on an expense — the
            # tracker's pie chart is for that group.
            if category.group != CategoryGroup.SPENDING:
                raise AppError("Expenses can only be categorised under Spending")
        return self._expenses.add(
            Expense(
                user_id=self._user_id,
                spend_date=data.spend_date,
                amount_pence=data.amount_pence,
                description=data.description,
                kind=data.kind,
                category_id=data.category_id,
            )
        )

    def delete(self, expense_id: int) -> None:
        expense = self._expenses.get(self._user_id, expense_id)
        if expense is None:
            raise NotFoundError(f"Expense {expense_id} not found")
        self._expenses.delete(expense)
