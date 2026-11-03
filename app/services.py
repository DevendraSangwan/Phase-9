import csv
import threading
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from app.config import CSV_COLUMNS, CSV_PATH
from app.models import Expense, ExpenseCreate, ExpenseUpdate


class StorageError(Exception):
    pass


class ExpenseService:
    def __init__(self, csv_path: Path = CSV_PATH) -> None:
        self.csv_path = csv_path
        self._lock = threading.RLock()

    def _ensure_file(self) -> None:
        if self.csv_path.exists():
            return
        try:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with self.csv_path.open("w", newline="", encoding="utf-8") as file:
                csv.DictWriter(file, fieldnames=CSV_COLUMNS).writeheader()
        except OSError as exc:
            raise StorageError(f"Unable to initialize expense storage: {exc}") from exc

    def _load(self) -> list[Expense]:
        self._ensure_file()
        try:
            with self.csv_path.open(newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != list(CSV_COLUMNS):
                    raise StorageError("Expense CSV has an invalid header.")

                expenses: list[Expense] = []
                for row in reader:
                    if None in row:
                        raise StorageError("Expense CSV contains a malformed row.")
                    expenses.append(Expense.model_validate(row))
                return expenses
        except (OSError, csv.Error, ValidationError, ValueError, TypeError) as exc:
            raise StorageError(f"Unable to read expense storage: {exc}") from exc

    def _save(self, expenses: list[Expense]) -> None:
        self._ensure_file()
        try:
            with self.csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                for expense in expenses:
                    writer.writerow(
                        {
                            **expense.model_dump(mode="json"),
                            "amount": expense.amount,
                        }
                    )
        except (OSError, csv.Error, ValueError) as exc:
            raise StorageError(f"Unable to write expense storage: {exc}") from exc

    def list_expenses(
        self,
        *,
        category: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        offset: int = 0,
        limit: int | None = 100,
        sort_by: str = "date",
        order: str = "desc",
    ) -> list[Expense]:
        with self._lock:
            expenses = self._load()

        if category is not None:
            expenses = [
                expense
                for expense in expenses
                if expense.category.casefold() == category.casefold()
            ]
        if start_date is not None:
            expenses = [expense for expense in expenses if expense.date >= start_date]
        if end_date is not None:
            expenses = [expense for expense in expenses if expense.date <= end_date]

        expenses.sort(
            key=lambda expense: getattr(expense, sort_by),
            reverse=order == "desc",
        )
        return expenses[offset:] if limit is None else expenses[offset : offset + limit]

    def get_expense(self, expense_id: int) -> Expense | None:
        with self._lock:
            return next(
                (expense for expense in self._load() if expense.id == expense_id),
                None,
            )

    def create_expense(self, expense: ExpenseCreate) -> Expense:
        with self._lock:
            expenses = self._load()
            next_id = max((item.id for item in expenses), default=0) + 1
            created = Expense(id=next_id, **expense.model_dump())
            self._save([*expenses, created])
            return created

    def update_expense(
        self, expense_id: int, expense: ExpenseUpdate
    ) -> Expense | None:
        with self._lock:
            expenses = self._load()
            for index, current in enumerate(expenses):
                if current.id == expense_id:
                    updated = Expense(id=expense_id, **expense.model_dump())
                    expenses[index] = updated
                    self._save(expenses)
                    return updated
            return None

    def delete_expense(self, expense_id: int) -> bool:
        with self._lock:
            expenses = self._load()
            remaining = [item for item in expenses if item.id != expense_id]
            if len(remaining) == len(expenses):
                return False
            self._save(remaining)
            return True
