from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=100)
    date: date
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("title", "category")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class ExpenseUpdate(ExpenseCreate):
    pass


class Expense(ExpenseCreate):
    id: int = Field(gt=0)


class MessageResponse(BaseModel):
    message: str


class StatisticsResponse(BaseModel):
    total: float
    average: float
    highest: float
    count: int
    average_daily: float
