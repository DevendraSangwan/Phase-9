# Expense Tracker API

A REST API built with FastAPI and Python for recording expenses in a CSV file and
viewing spending summaries. It includes CRUD operations, validation, filtering,
sorting, pagination, and analytics.

## Features

- Create, list, retrieve, update, and delete expenses
- Validate required fields, positive amounts, and ISO-formatted dates
- Filter by category and date range; sort and paginate expense lists
- View monthly totals, category totals, and overall statistics
- Persist data in `data/expenses.csv`
- Browse and try the API through the generated Swagger UI

## Requirements

- Python 3.10 or later
- pip

## Setup and run

From the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The API is available at <http://127.0.0.1:8000>. Open
<http://127.0.0.1:8000/docs> for interactive Swagger documentation.

## Project structure

```text
expense_tracker_api/
├── app/
│   ├── __init__.py
│   ├── analytics.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── data/
│   └── expenses.csv
├── tests/
│   └── test_api.py
├── .gitignore
├── README.md
└── requirements.txt
```

`models.py` defines validated Pydantic request/response models. `services.py`
handles CSV storage and CRUD logic, `analytics.py` calculates reports with
Pandas and NumPy, and `main.py` exposes the HTTP endpoints. The CSV file is
created automatically if it does not exist.

## Expense format

```json
{
  "title": "Lunch",
  "amount": 250,
  "category": "Food",
  "date": "2026-09-25",
  "notes": "Office lunch"
}
```

The `notes` field is optional. Amounts must be greater than zero; titles and
categories cannot be blank. Dates use `YYYY-MM-DD`.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/expenses` | Add an expense (returns a success message) |
| `GET` | `/expenses` | List expenses |
| `GET` | `/expenses/{expense_id}` | Get one expense |
| `PUT` | `/expenses/{expense_id}` | Replace an expense |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense |
| `GET` | `/reports/monthly` | Totals grouped by `YYYY-MM` |
| `GET` | `/reports/category` | Totals grouped by category |
| `GET` | `/reports/statistics` | Total, average, highest, count, and average per active day |

List expenses can be filtered with `category`, `start_date`, and `end_date`.
Pagination uses `offset` (default `0`) and `limit` (default `100`, maximum
`500`). Sorting uses `sort_by` (`id`, `title`, `amount`, `category`, or `date`)
and `order` (`asc` or `desc`).

Example:

```text
GET /expenses?category=Food&start_date=2026-09-01&sort_by=amount&order=desc
```

Missing expense IDs return `404`; invalid request data returns `422`; CSV
storage failures return `500`.

## Tests

```bash
pytest
```
# Phase-9
