from datetime import date

from pydantic import BaseModel

from api.schemas.expense import ExpenseRead


class WeekSummary(BaseModel):
    index: int
    start: date
    end: date
    allowance_pence: int
    spent_pence: int
    saved_pence: int
    expenses: list[ExpenseRead]


class CategoryBreakdownItem(BaseModel):
    """How much was spent on one Spending category this month. category_id
    is None for the "uncategorised" bucket — REGULAR expenses logged without
    a category assignment."""

    category_id: int | None
    name: str
    amount_pence: int


class MonthSummary(BaseModel):
    year: int
    month: int
    spending_budget_pence: int
    total_spent_pence: int
    total_saved_pence: int
    weeks: list[WeekSummary]
    category_breakdown: list[CategoryBreakdownItem]
