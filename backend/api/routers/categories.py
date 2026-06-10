from fastapi import APIRouter, status

from api.dependencies.services import CategoryServiceDep
from api.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(service: CategoryServiceDep):
    return service.list_all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, service: CategoryServiceDep):
    return service.create(payload)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, service: CategoryServiceDep):
    return service.update(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, service: CategoryServiceDep):
    service.delete(category_id)
