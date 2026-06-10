from pydantic import BaseModel, ConfigDict, Field

from api.shared.enums import CategoryGroup


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    group: CategoryGroup
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    sort_order: int | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group: CategoryGroup
    sort_order: int
