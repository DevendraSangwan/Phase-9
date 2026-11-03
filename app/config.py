from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CSV_PATH = DATA_DIR / "expenses.csv"

CSV_COLUMNS = ("id", "title", "amount", "category", "date", "notes")
