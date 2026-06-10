from typing import Annotated

from fastapi import APIRouter, Path

from api.dependencies.services import BudgetServiceDep
from api.schemas.budget import (
    BudgetCellUpdate,
    BudgetEntryRead,
    CopyForwardResult,
    YearView,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])

Month = Annotated[int, Path(ge=1, le=12)]
Year = Annotated[int, Path(ge=2000, le=2100)]


@router.get("/{year}", response_model=YearView)
def get_year_view(year: Year, service: BudgetServiceDep):
    return service.get_year_view(year)


@router.put("/{year}/{month}/categories/{category_id}", response_model=BudgetEntryRead)
def set_budget_amount(
    year: Year,
    month: Month,
    category_id: int,
    payload: BudgetCellUpdate,
    service: BudgetServiceDep,
):
    return service.set_amount(category_id, year, month, payload.amount_pence)


@router.post("/{year}/{month}/copy-forward", response_model=CopyForwardResult)
def copy_forward(year: Year, month: Month, service: BudgetServiceDep):
    months_filled = service.copy_forward(year, month)
    return CopyForwardResult(source_year=year, source_month=month, months_filled=months_filled)
