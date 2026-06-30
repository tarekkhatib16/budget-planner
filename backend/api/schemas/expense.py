from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from api.shared.enums import ExpenseKind


class ExpenseCreate(BaseModel):
    spend_date: date
    amount_pence: int = Field(gt=0)
    description: str | None = Field(default=None, max_length=255)
    kind: ExpenseKind = ExpenseKind.REGULAR


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spend_date: date
    amount_pence: int
    description: str | None
    kind: ExpenseKind
