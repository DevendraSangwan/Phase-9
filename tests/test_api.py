from fastapi.testclient import TestClient

from app.main import app
from app.services import ExpenseService


def test_expense_crud_and_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.main.expense_service", ExpenseService(tmp_path / "expenses.csv")
    )
    client = TestClient(app)
    first = {
        "title": "Lunch",
        "amount": 250,
        "category": "Food",
        "date": "2026-09-20",
        "notes": "Office lunch",
    }
    second = {
        "title": "Metro",
        "amount": 80,
        "category": "Travel",
        "date": "2026-09-21",
        "notes": None,
    }

    response = client.post("/expenses", json=first)
    assert response.status_code == 201
    assert response.json() == {"message": "Expense added successfully"}
    client.post("/expenses", json=second)

    expenses = client.get("/expenses").json()
    assert [item["title"] for item in expenses] == ["Metro", "Lunch"]
    assert client.get("/expenses/1").json()["title"] == "Lunch"
    assert client.get("/expenses?category=food").json()[0]["id"] == 1
    assert client.get("/reports/monthly").json() == {"2026-09": 330.0}
    assert client.get("/reports/category").json() == {"Food": 250.0, "Travel": 80.0}
    assert client.get("/reports/statistics").json() == {
        "total": 330.0,
        "average": 165.0,
        "highest": 250.0,
        "count": 2,
        "average_daily": 165.0,
    }

    updated = {**first, "title": "Updated lunch"}
    assert client.put("/expenses/1", json=updated).json()["title"] == "Updated lunch"
    assert client.delete("/expenses/2").status_code == 200
    assert [item["id"] for item in client.get("/expenses").json()] == [1]


def test_invalid_expense_and_missing_id(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.main.expense_service", ExpenseService(tmp_path / "expenses.csv")
    )
    client = TestClient(app)

    invalid = {
        "title": "Coffee",
        "amount": 0,
        "category": "Food",
        "date": "2026-09-25",
    }
    assert client.post("/expenses", json=invalid).status_code == 422
    assert client.get("/expenses/999").status_code == 404
    assert client.put("/expenses/999", json={**invalid, "amount": 10}).status_code == 404
    assert client.delete("/expenses/999").status_code == 404


def test_empty_reports_and_date_range_validation(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.main.expense_service", ExpenseService(tmp_path / "expenses.csv")
    )
    client = TestClient(app)

    assert client.get("/reports/monthly").json() == {}
    assert client.get("/reports/category").json() == {}
    assert client.get("/reports/statistics").json()["count"] == 0
    assert (
        client.get(
            "/expenses?start_date=2026-09-30&end_date=2026-09-01"
        ).status_code
        == 422
    )
