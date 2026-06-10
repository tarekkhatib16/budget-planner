from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import Category
from api.shared.enums import CategoryGroup


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Category]:
        stmt = select(Category).order_by(Category.sort_order, Category.name)
        return list(self._session.scalars(stmt))

    def get(self, category_id: int) -> Category | None:
        return self._session.get(Category, category_id)

    def find_by_name(self, name: str, group: CategoryGroup) -> Category | None:
        stmt = select(Category).where(Category.name == name, Category.group == group)
        return self._session.scalars(stmt).first()

    def add(self, category: Category) -> Category:
        self._session.add(category)
        self._session.flush()
        return category

    def delete(self, category: Category) -> None:
        self._session.delete(category)
        self._session.flush()
