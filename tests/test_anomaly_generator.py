
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database" / "smartspend.db"


@pytest.fixture
def connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def get_anomaly(connection, scenario):
    return connection.execute(
        """
        SELECT *
        FROM anomaly_ground_truth
        WHERE scenario_type = ?
        """,
        (scenario,),
    ).fetchone()


def test_transfer_double_count_scenario(connection):
    record = get_anomaly(connection, "TRANSFER_DOUBLE_COUNT")

    assert record is not None
    assert record["expected_decision"] == "EXCLUDE_FROM_EXPENSE_TOTAL"


def test_refund_scenario(connection):
    record = get_anomaly(connection, "REFUND_AS_NEW_EXPENSE")

    assert record is not None
    assert record["expected_decision"] == "TREAT_AS_REFUND_CREDIT"


def test_recurring_payment_skipped_scenario(connection):
    record = get_anomaly(connection, "RECURRING_PAYMENT_SKIPPED")

    assert record is not None
    assert record["expected_decision"] == "FLAG_MISSING_RECURRING_PAYMENT"


def test_timezone_boundary_conversion(connection):
    transaction = connection.execute(
        """
        SELECT transaction_date
        FROM transactions
        WHERE transaction_id = 'ANOM-TXN-004'
        """
    ).fetchone()

    assert transaction is not None

    original_time = datetime.fromisoformat(transaction["transaction_date"])
    utc_time = original_time.astimezone(timezone.utc)

    assert utc_time.date().isoformat() == "2026-01-01"


def test_invalid_budget_category_scenario(connection):
    record = get_anomaly(connection, "INVALID_BUDGET_CATEGORY")

    assert record is not None
    assert record["expected_decision"] == "REJECT_INVALID_CATEGORY"
    assert record["transaction_id"] is None


def test_all_five_anomaly_scenarios_exist(connection):
    count = connection.execute(
        "SELECT COUNT(*) FROM anomaly_ground_truth"
    ).fetchone()[0]

    assert count == 5
