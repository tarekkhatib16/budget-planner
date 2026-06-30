from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.models import Expense
from api.shared.enums import ExpenseKind


class ExpenseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_between(
        self,
        user_id: int,
        start: date,
        end: date,
        kind: ExpenseKind | None = None,
    ) -> list[Expense]:
        stmt = (
            select(Expense)
            .where(
                Expense.user_id == user_id,
                Expense.spend_date >= start,
                Expense.spend_date <= end,
            )
            .order_by(Expense.spend_date, Expense.id)
        )
        if kind is not None:
            stmt = stmt.where(Expense.kind == kind)
        return list(self._session.scalars(stmt))

    def category_totals_for_month(
        self, user_id: int, year: int, month: int
    ) -> dict[int | None, int]:
        """Sum of REGULAR expense amounts grouped by category for one month.

        Returns {category_id (or None for uncategorised): amount_pence}.
        """
        from api.utils.dates import month_bounds

        start, end = month_bounds(year, month)
        stmt = (
            select(Expense.category_id, func.sum(Expense.amount_pence))
            .where(
                Expense.user_id == user_id,
                Expense.kind == ExpenseKind.REGULAR,
                Expense.spend_date >= start,
                Expense.spend_date <= end,
            )
            .group_by(Expense.category_id)
        )
        return {
            (int(cat_id) if cat_id is not None else None): int(total or 0)
            for cat_id, total in self._session.execute(stmt)
        }

    def monthly_totals(
        self, user_id: int, year: int, kind: ExpenseKind
    ) -> dict[int, int]:
        """Sum of amount_pence per month for one kind over one year."""
        # extract(month) works on both SQLite and Postgres for Date columns.
        month_col = func.extract("month", Expense.spend_date)
        year_col = func.extract("year", Expense.spend_date)
        stmt = (
            select(month_col, func.sum(Expense.amount_pence))
            .where(
                Expense.user_id == user_id,
                Expense.kind == kind,
                year_col == year,
            )
            .group_by(month_col)
        )
        return {int(month): int(total or 0) for month, total in self._session.execute(stmt)}

    def get(self, user_id: int, expense_id: int) -> Expense | None:
        stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        return self._session.scalars(stmt).first()

    def add(self, expense: Expense) -> Expense:
        self._session.add(expense)
        self._session.flush()
        return expense

    def delete(self, expense: Expense) -> None:
        self._session.delete(expense)
        self._session.flush()
