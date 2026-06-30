from datetime import date

from sqlalchemy import Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from api.shared.enums import ExpenseKind
from database.base import Base


class Expense(Base):
    """A single logged spend.

    REGULAR expenses are bucketed into a week of their month for the tracker
    (against the SPENDING budget). UNUSUAL expenses are one-off costs shown
    in their own tab and summed per month on the budget summary.

    `category_id` optionally links a REGULAR expense to one of the user's
    SPENDING categories so the tracker can show a per-category breakdown.
    ON DELETE SET NULL: removing a category turns its past expenses into
    "uncategorised" rather than deleting them.
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), index=True, nullable=True
    )
    spend_date: Mapped[date] = mapped_column(Date, index=True)
    amount_pence: Mapped[int]
    description: Mapped[str | None] = mapped_column(String(255), default=None)
    kind: Mapped[ExpenseKind] = mapped_column(
        SAEnum(ExpenseKind, values_callable=lambda e: [m.value for m in e]),
        default=ExpenseKind.REGULAR,
        server_default=ExpenseKind.REGULAR.value,
        index=True,
    )
