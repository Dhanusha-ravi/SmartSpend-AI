import sqlite3

from config.settings import DATABASE_PATH


def validate_data():
    connection = sqlite3.connect(DATABASE_PATH)

    checks = {
        "Total transactions": """
            SELECT COUNT(*) FROM transactions
        """,

        "Duplicate transaction IDs": """
            SELECT COUNT(*) FROM (
                SELECT transaction_id
                FROM transactions
                GROUP BY transaction_id
                HAVING COUNT(*) > 1
            )
        """,

        "Transactions without ground truth": """
            SELECT COUNT(*)
            FROM transactions t
            LEFT JOIN transaction_category_ground_truth g
            ON t.transaction_id = g.transaction_id
            WHERE g.transaction_id IS NULL
        """,

        "Duplicate ground truth records": """
            SELECT COUNT(*) FROM (
                SELECT transaction_id
                FROM transaction_category_ground_truth
                GROUP BY transaction_id
                HAVING COUNT(*) > 1
            )
        """,

        "Invalid transaction amounts": """
            SELECT COUNT(*) FROM transactions
            WHERE amount <= 0
        """,

        "Missing descriptions": """
            SELECT COUNT(*) FROM transactions
            WHERE description IS NULL OR TRIM(description) = ''
        """,

        "Missing transaction dates": """
            SELECT COUNT(*) FROM transactions
            WHERE transaction_date IS NULL
               OR date(transaction_date) IS NULL
        """,

        "Missing transaction categories": """
            SELECT COUNT(*) FROM transactions
            WHERE category_code IS NULL
        """,

        "Invalid transaction types": """
            SELECT COUNT(*) FROM transactions
            WHERE transaction_type NOT IN ('DEBIT', 'CREDIT')
        """,

        "Invalid transaction statuses": """
            SELECT COUNT(*) FROM transactions
            WHERE status NOT IN (
                'COMPLETED', 'PENDING', 'FAILED', 'REVERSED'
            )
        """,

        "Missing ground truth categories": """
            SELECT COUNT(*)
            FROM transaction_category_ground_truth
            WHERE actual_category_code IS NULL
        """
    }

    try:
        print("\nSMARTSPEND DATA VALIDATION")
        print("=" * 45)

        for name, query in checks.items():
            result = connection.execute(query).fetchone()[0]
            print(f"{name}: {result}")

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("Foreign key errors:", len(foreign_key_errors))
        print("\nValidation completed!")

    finally:
        connection.close()


if __name__ == "__main__":
    validate_data()