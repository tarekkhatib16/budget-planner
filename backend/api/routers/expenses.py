from typing import Annotated

from fastapi import APIRouter, Query, status

from api.dependencies.services import ExpenseServiceDep
from api.schemas.expense import ExpenseCreate, ExpenseRead

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    year: Annotated[int, Query(ge=2000, le=2100)],
    month: Annotated[int, Query(ge=1, le=12)],
    service: ExpenseServiceDep,
):
    return service.list_for_month(year, month)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, service: ExpenseServiceDep):
    return service.create(payload)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, service: ExpenseServiceDep):
    service.delete(expense_id)
