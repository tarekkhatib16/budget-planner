from api.exceptions.errors import NotFoundError
from api.models import Expense
from api.repositories.expense_repository import ExpenseRepository
from api.schemas.expense import ExpenseCreate
from api.utils.dates import month_bounds


class ExpenseService:
    def __init__(self, expenses: ExpenseRepository, user_id: int) -> None:
        self._expenses = expenses
        self._user_id = user_id

    def list_for_month(self, year: int, month: int) -> list[Expense]:
        return self._expenses.list_between(self._user_id, *month_bounds(year, month))

    def create(self, data: ExpenseCreate) -> Expense:
        return self._expenses.add(
            Expense(
                user_id=self._user_id,
                spend_date=data.spend_date,
                amount_pence=data.amount_pence,
                description=data.description,
            )
        )

    def delete(self, expense_id: int) -> None:
        expense = self._expenses.get(self._user_id, expense_id)
        if expense is None:
            raise NotFoundError(f"Expense {expense_id} not found")
        self._expenses.delete(expense)
