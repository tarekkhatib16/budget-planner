from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import BudgetEntry


class BudgetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_year(self, year: int) -> list[BudgetEntry]:
        stmt = select(BudgetEntry).where(BudgetEntry.year == year)
        return list(self._session.scalars(stmt))

    def list_for_month(self, year: int, month: int) -> list[BudgetEntry]:
        stmt = select(BudgetEntry).where(
            BudgetEntry.year == year, BudgetEntry.month == month
        )
        return list(self._session.scalars(stmt))

    def get_cell(self, category_id: int, year: int, month: int) -> BudgetEntry | None:
        stmt = select(BudgetEntry).where(
            BudgetEntry.category_id == category_id,
            BudgetEntry.year == year,
            BudgetEntry.month == month,
        )
        return self._session.scalars(stmt).first()

    def upsert(self, category_id: int, year: int, month: int, amount_pence: int) -> BudgetEntry:
        entry = self.get_cell(category_id, year, month)
        if entry is None:
            entry = BudgetEntry(category_id=category_id, year=year, month=month)
            self._session.add(entry)
        entry.amount_pence = amount_pence
        self._session.flush()
        return entry
