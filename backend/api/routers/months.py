from typing import Annotated

from fastapi import APIRouter, Path

from api.dependencies.services import MonthServiceDep
from api.schemas.month import MonthSummary

router = APIRouter(prefix="/months", tags=["months"])


@router.get("/{year}/{month}", response_model=MonthSummary)
def get_month_summary(
    year: Annotated[int, Path(ge=2000, le=2100)],
    month: Annotated[int, Path(ge=1, le=12)],
    service: MonthServiceDep,
):
    return service.get_summary(year, month)
