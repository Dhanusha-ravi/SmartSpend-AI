from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
GROUND_TRUTH_DIR = BASE_DIR / "data" / "ground_truth"
EXPORTS_DIR = BASE_DIR / "data" / "exports"

# Database
DATABASE_PATH = BASE_DIR / "database" / "smartspend.db"

# Dataset configuration
NUM_USERS = 1000
NUM_TRANSACTIONS = 500_000
NUM_MONTHS = 12

# Reproducibility
RANDOM_SEED = 42

# Currency
DEFAULT_CURRENCY = "INR"
