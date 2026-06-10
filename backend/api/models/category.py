from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.shared.enums import CategoryGroup
from database.base import Base


class Category(Base):
    """A row in the yearly budget grid, e.g. "Groceries" under SPENDING."""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", "group", name="uq_category_name_group"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    group: Mapped[CategoryGroup] = mapped_column(
        SAEnum(CategoryGroup, values_callable=lambda e: [m.value for m in e])
    )
    sort_order: Mapped[int] = mapped_column(default=0)

    budget_entries: Mapped[list["BudgetEntry"]] = relationship(  # noqa: F821
        back_populates="category", cascade="all, delete-orphan"
    )
