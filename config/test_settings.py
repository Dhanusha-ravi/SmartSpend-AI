from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "smartspend_test.db"

NUM_USERS = 1000
NUM_TRANSACTIONS = 500_000
NUM_MONTHS = 12

RANDOM_SEED = 42
DEFAULT_CURRENCY = "INR"