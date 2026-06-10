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


class MonthSummary(BaseModel):
    year: int
    month: int
    spending_budget_pence: int
    total_spent_pence: int
    total_saved_pence: int
    weeks: list[WeekSummary]
