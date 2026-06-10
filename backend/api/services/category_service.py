from api.exceptions.errors import ConflictError, NotFoundError
from api.models import Category
from api.repositories.category_repository import CategoryRepository
from api.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, categories: CategoryRepository, user_id: int) -> None:
        self._categories = categories
        self._user_id = user_id

    def list_all(self) -> list[Category]:
        return self._categories.list_all(self._user_id)

    def create(self, data: CategoryCreate) -> Category:
        if self._categories.find_by_name(self._user_id, data.name, data.group):
            raise ConflictError(f"Category '{data.name}' already exists in {data.group.value}")
        return self._categories.add(
            Category(
                user_id=self._user_id,
                name=data.name,
                group=data.group,
                sort_order=data.sort_order,
            )
        )

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self._get_or_raise(category_id)
        if data.name is not None:
            existing = self._categories.find_by_name(self._user_id, data.name, category.group)
            if existing and existing.id != category.id:
                raise ConflictError(
                    f"Category '{data.name}' already exists in {category.group.value}"
                )
            category.name = data.name
        if data.sort_order is not None:
            category.sort_order = data.sort_order
        return category

    def delete(self, category_id: int) -> None:
        self._categories.delete(self._get_or_raise(category_id))

    def _get_or_raise(self, category_id: int) -> Category:
        category = self._categories.get(self._user_id, category_id)
        if category is None:
            raise NotFoundError(f"Category {category_id} not found")
        return category
