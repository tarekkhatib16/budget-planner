from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class BudgetEntry(Base):
    """The planned amount for one category in one month, in whole pence."""

    __tablename__ = "budget_entries"
    __table_args__ = (
        UniqueConstraint("category_id", "year", "month", name="uq_budget_cell"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    year: Mapped[int] = mapped_column(index=True)
    month: Mapped[int]
    amount_pence: Mapped[int] = mapped_column(default=0)

    category: Mapped["Category"] = relationship(back_populates="budget_entries")  # noqa: F821
