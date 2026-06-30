from pydantic import BaseModel, ConfigDict, Field

from api.shared.enums import CategoryGroup


class BudgetCellUpdate(BaseModel):
    amount_pence: int = Field(ge=0)


class BudgetEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    year: int
    month: int
    amount_pence: int


class CopyForwardResult(BaseModel):
    source_year: int
    source_month: int
    months_filled: int


class CategoryRow(BaseModel):
    """One category with its 12 monthly amounts (index 0 = January)."""

    category_id: int
    name: str
    amounts_pence: list[int]


class GroupSection(BaseModel):
    """One section of the grid (e.g. BILLS) with its per-month totals."""

    group: CategoryGroup
    rows: list[CategoryRow]
    totals_pence: list[int]


class YearView(BaseModel):
    year: int
    sections: list[GroupSection]
    # Actual unusual expenses summed per month (one-off costs like holidays
    # that aren't planned in a category but reduce monthly savings).
    monthly_unusual_pence: list[int]
    monthly_savings_pence: list[int]
    cumulative_savings_pence: list[int]
