from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Expense(Base):
    """A single logged spend, bucketed into a week of its month for the tracker."""

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    spend_date: Mapped[date] = mapped_column(Date, index=True)
    amount_pence: Mapped[int]
    description: Mapped[str | None] = mapped_column(String(255), default=None)
