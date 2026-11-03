import numpy as np
import pandas as pd

from app.models import Expense, StatisticsResponse


def _dataframe(expenses: list[Expense]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "amount": expense.amount,
                "category": expense.category,
                "date": expense.date,
            }
            for expense in expenses
        ],
        columns=["amount", "category", "date"],
    )


def monthly_summary(expenses: list[Expense]) -> dict[str, float]:
    frame = _dataframe(expenses)
    if frame.empty:
        return {}
    frame["month"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m")
    totals = frame.groupby("month")["amount"].sum().sort_index()
    return {month: round(float(total), 2) for month, total in totals.items()}


def category_summary(expenses: list[Expense]) -> dict[str, float]:
    frame = _dataframe(expenses)
    if frame.empty:
        return {}
    totals = frame.groupby("category")["amount"].sum().sort_index()
    return {category: round(float(total), 2) for category, total in totals.items()}


def calculate_statistics(expenses: list[Expense]) -> StatisticsResponse:
    if not expenses:
        return StatisticsResponse(
            total=0, average=0, highest=0, count=0, average_daily=0
        )

    amounts = np.array([expense.amount for expense in expenses], dtype=float)
    active_days = len({expense.date for expense in expenses})
    return StatisticsResponse(
        total=round(float(np.sum(amounts)), 2),
        average=round(float(np.mean(amounts)), 2),
        highest=round(float(np.max(amounts)), 2),
        count=len(expenses),
        average_daily=round(float(np.sum(amounts) / active_days), 2),
    )
