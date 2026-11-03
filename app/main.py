from datetime import date
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.analytics import calculate_statistics, category_summary, monthly_summary
from app.models import (
    Expense,
    ExpenseCreate,
    ExpenseUpdate,
    MessageResponse,
    StatisticsResponse,
)
from app.services import ExpenseService, StorageError
from app.utils import validate_date_range

app = FastAPI(
    title="Expense Tracker API",
    description="A CSV-backed API for recording expenses and viewing spending reports.",
    version="1.0.0",
)
expense_service = ExpenseService()


@app.exception_handler(StorageError)
async def handle_storage_error(_: Request, exc: StorageError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.post(
    "/expenses",
    response_model=MessageResponse,
    status_code=201,
    tags=["Expenses"],
)
def create_expense(expense: ExpenseCreate) -> MessageResponse:
    expense_service.create_expense(expense)
    return MessageResponse(message="Expense added successfully")


@app.get("/expenses", response_model=list[Expense], tags=["Expenses"])
def list_expenses(
    category: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    start_date: date | None = None,
    end_date: date | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    sort_by: Literal["id", "title", "amount", "category", "date"] = "date",
    order: Literal["asc", "desc"] = "desc",
) -> list[Expense]:
    validate_date_range(start_date, end_date)
    return expense_service.list_expenses(
        category=category,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )


@app.get("/expenses/{expense_id}", response_model=Expense, tags=["Expenses"])
def get_expense(expense_id: int) -> Expense:
    expense = expense_service.get_expense(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/expenses/{expense_id}", response_model=Expense, tags=["Expenses"])
def update_expense(expense_id: int, payload: ExpenseUpdate) -> Expense:
    expense = expense_service.update_expense(expense_id, payload)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete(
    "/expenses/{expense_id}",
    response_model=MessageResponse,
    tags=["Expenses"],
)
def delete_expense(expense_id: int) -> MessageResponse:
    if not expense_service.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return MessageResponse(message="Expense deleted successfully")


@app.get("/reports/monthly", response_model=dict[str, float], tags=["Reports"])
def get_monthly_report() -> dict[str, float]:
    return monthly_summary(expense_service.list_expenses(limit=None))


@app.get("/reports/category", response_model=dict[str, float], tags=["Reports"])
def get_category_report() -> dict[str, float]:
    expenses = expense_service.list_expenses(limit=None)
    return category_summary(expenses)


@app.get(
    "/reports/statistics",
    response_model=StatisticsResponse,
    tags=["Reports"],
)
def get_statistics() -> StatisticsResponse:
    expenses = expense_service.list_expenses(limit=None)
    return calculate_statistics(expenses)
