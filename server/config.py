from pathlib import Path

# found absolute path to project
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "database.db"

DB_URL=f"sqlite:///{DB_PATH}"
PWD_SALT=b"qwerty"
PWD_ITERATIONS=100_000