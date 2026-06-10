from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Expense


class ExpenseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_between(self, start: date, end: date) -> list[Expense]:
        stmt = (
            select(Expense)
            .where(Expense.spend_date >= start, Expense.spend_date <= end)
            .order_by(Expense.spend_date, Expense.id)
        )
        return list(self._session.scalars(stmt))

    def get(self, expense_id: int) -> Expense | None:
        return self._session.get(Expense, expense_id)

    def add(self, expense: Expense) -> Expense:
        self._session.add(expense)
        self._session.flush()
        return expense

    def delete(self, expense: Expense) -> None:
        self._session.delete(expense)
        self._session.flush()
