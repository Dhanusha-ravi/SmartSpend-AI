import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH


def generate_recurring_test_transactions():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Check whether test IDs already exist
        existing = connection.execute("""
            SELECT COUNT(*)
            FROM transactions
            WHERE transaction_id LIKE 'TESTREC%'
        """).fetchone()[0]

        if existing > 0:
            print("Test transactions already exist. No changes made.")
            return

        recurring_transactions = []

        for month in range(1, 13):
            transaction_id = f"TESTREC{month:03d}"
            ground_truth_id = f"GTREC{month:03d}"
            transaction_date = f"2025-{month:02d}-05"

            recurring_transactions.append((
                transaction_id,
                "ACC000001",
                "M009",
                "ENTERTAINMENT",
                transaction_date,
                "Netflix Monthly Subscription",
                649.00,
                "DEBIT",
                "UPI",
                "INR",
                "COMPLETED",
                f"{transaction_date} 10:00:00",
                ground_truth_id,
                "ENTERTAINMENT",
                "SYNTHETIC_TEST",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        with connection:
            for row in recurring_transactions:
                connection.execute("""
                    INSERT INTO transactions (
                        transaction_id, account_id, merchant_id,
                        category_code, transaction_date, description,
                        amount, transaction_type, payment_method,
                        currency, status, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, row[:12])

                connection.execute("""
                    INSERT INTO transaction_category_ground_truth (
                        ground_truth_id, transaction_id,
                        actual_category_code, verified_by, verified_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row[12], row[0], row[13], row[14], row[15]
                ))

        print("Successfully created 12 test transactions.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_recurring_test_transactions()