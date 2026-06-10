from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Category
from api.shared.enums import CategoryGroup


class CategoryRepository:
    """All queries are scoped to a user: one user can never see or touch
    another user's rows."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self, user_id: int) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.sort_order, Category.name)
        )
        return list(self._session.scalars(stmt))

    def get(self, user_id: int, category_id: int) -> Category | None:
        stmt = select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
        return self._session.scalars(stmt).first()

    def find_by_name(self, user_id: int, name: str, group: CategoryGroup) -> Category | None:
        stmt = select(Category).where(
            Category.user_id == user_id,
            Category.name == name,
            Category.group == group,
        )
        return self._session.scalars(stmt).first()

    def add(self, category: Category) -> Category:
        self._session.add(category)
        self._session.flush()
        return category

    def delete(self, category: Category) -> None:
        self._session.delete(category)
        self._session.flush()
