
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "database" / "smartspend_test.db"

TEST_TRANSACTIONS = [
    {
        "id": "ANOM-TXN-001",
        "date": "2025-11-01",
        "description": "TEST TRANSFER DOUBLE COUNT",
        "amount": 5000.00,
        "type": "DEBIT",
        "category": "TRANSFER",
        "scenario": "TRANSFER_DOUBLE_COUNT",
        "decision": "EXCLUDE_FROM_EXPENSE_TOTAL",
        "issue": "Transfer must not be counted as household spending twice.",
        "severity": "HIGH",
    },
    {
        "id": "ANOM-TXN-002",
        "date": "2025-11-02",
        "description": "TEST REFUND",
        "amount": 1200.00,
        "type": "CREDIT",
        "category": "SHOPPING",
        "scenario": "REFUND_AS_NEW_EXPENSE",
        "decision": "TREAT_AS_REFUND_CREDIT",
        "issue": "Refund must reduce net spending, not create a new expense.",
        "severity": "HIGH",
    },
    {
        "id": "ANOM-TXN-003",
        "date": "2025-11-03",
        "description": "TEST MISSED MONTHLY SUBSCRIPTION",
        "amount": 649.00,
        "type": "DEBIT",
        "category": "ENTERTAINMENT",
        "scenario": "RECURRING_PAYMENT_SKIPPED",
        "decision": "FLAG_MISSING_RECURRING_PAYMENT",
        "issue": "Expected recurring payment is missing from its series.",
        "severity": "MEDIUM",
    },
    {
        "id": "ANOM-TXN-004",
        "date": "2025-12-31T23:30:00-05:00",
        "description": "TEST TIMEZONE BOUNDARY",
        "amount": 250.00,
        "type": "DEBIT",
        "category": "FOOD",
        "scenario": "TIMEZONE_BOUNDARY",
        "decision": "NORMALIZE_TO_UTC_DATE",
        "issue": "Local transaction time converts to the next UTC calendar date.",
        "severity": "MEDIUM",
    },
]


def generate_anomalies():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        account = connection.execute(
            "SELECT account_id FROM account ORDER BY account_id LIMIT 1"
        ).fetchone()

        if account is None:
            raise ValueError(
                "No account found. Generate user and account data first."
            )

        account_id = account[0]
        created_at = datetime.now(timezone.utc).isoformat()

        for item in TEST_TRANSACTIONS:
            connection.execute(
                """
                INSERT OR IGNORE INTO transactions (
                    transaction_id, account_id, merchant_id,
                    category_code, transaction_date, description,
                    amount, transaction_type, payment_method,
                    currency, status, created_at
                )
                VALUES (?, ?, NULL, ?, ?, ?, ?, ?, 'TEST',
                        'INR', 'COMPLETED', ?)
                """,
                (
                    item["id"],
                    account_id,
                    item["category"],
                    item["date"],
                    item["description"],
                    item["amount"],
                    item["type"],
                    created_at,
                ),
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO transaction_category_ground_truth (
                    ground_truth_id,
                    transaction_id,
                    actual_category_code,
                    verified_by,
                    verified_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    f"ANOM-GT-{item['id']}",
                    item["id"],
                    item["category"],
                    "ANOMALY_TEST_FIXTURE",
                    created_at,
                ),
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO anomaly_ground_truth (
                    anomaly_id, scenario_type, transaction_id,
                    expected_decision, issue_description,
                    severity, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["scenario"],
                    item["id"],
                    item["decision"],
                    item["issue"],
                    item["severity"],
                    created_at,
                ),
            )

        # Invalid category is recorded as a rejected case.
        # We do not insert an invalid budget row because of the foreign key.
        connection.execute(
            """
            INSERT OR IGNORE INTO anomaly_ground_truth (
                anomaly_id, scenario_type, transaction_id,
                expected_decision, issue_description,
                severity, created_at
            )
            VALUES (?, ?, NULL, ?, ?, ?, ?)
            """,
            (
                "ANOM-005",
                "INVALID_BUDGET_CATEGORY",
                "REJECT_INVALID_CATEGORY",
                "A budget referencing an unknown category must be rejected.",
                "HIGH",
                created_at,
            ),
        )

        connection.commit()

        print("Anomaly test data generated successfully!")

        results = connection.execute(
            """
            SELECT scenario_type, expected_decision, severity
            FROM anomaly_ground_truth
            ORDER BY anomaly_id
            """
        ).fetchall()

        for result in results:
            print(result)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_anomalies()
