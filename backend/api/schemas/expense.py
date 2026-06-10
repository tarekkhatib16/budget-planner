from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    spend_date: date
    amount_pence: int = Field(gt=0)
    description: str | None = Field(default=None, max_length=255)


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spend_date: date
    amount_pence: int
    description: str | None
