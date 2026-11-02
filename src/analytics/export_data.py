import sqlite3
import json
import pandas as pd

from config.settings import DATABASE_PATH, EXPORTS_DIR


def export_project_data():
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        # 1. Export transactions to CSV
        transactions = pd.read_sql_query(
            "SELECT * FROM transactions",
            connection
        )

        transactions.to_csv(
            EXPORTS_DIR / "transactions.csv",
            index=False
        )

        print("Transactions CSV exported:", len(transactions))

        # 2. Export ground truth to CSV
        ground_truth = pd.read_sql_query(
            "SELECT * FROM transaction_category_ground_truth",
            connection
        )

        ground_truth.to_csv(
            EXPORTS_DIR / "ground_truth.csv",
            index=False
        )

        print("Ground truth CSV exported:", len(ground_truth))

        # 3. Export budgets to CSV
        budgets = pd.read_sql_query(
            "SELECT * FROM budget",
            connection
        )

        budgets.to_csv(
            EXPORTS_DIR / "budgets.csv",
            index=False
        )

        print("Budgets CSV exported:", len(budgets))

        # 4. Export recurring matches to CSV
        recurring_matches = pd.read_sql_query(
            "SELECT * FROM transaction_recurring_match",
            connection
        )

        recurring_matches.to_csv(
            EXPORTS_DIR / "recurring_matches.csv",
            index=False
        )

        print("Recurring matches CSV exported:", len(recurring_matches))

        # 5. Create JSON summary
        category_distribution = pd.read_sql_query("""
            SELECT category_code, COUNT(*) AS transaction_count
            FROM transactions
            GROUP BY category_code
            ORDER BY transaction_count DESC
        """, connection)

        summary = {
            "project": "SmartSpend-AI",
            "dataset_period": "2025-01-01 to 2025-12-31",
            "total_transactions": len(transactions),
            "total_ground_truth_records": len(ground_truth),
            "total_budgets": len(budgets),
            "total_recurring_matches": len(recurring_matches),
            "category_distribution": category_distribution.to_dict(
                orient="records"
            )
        }

        with open(
            EXPORTS_DIR / "project_summary.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(summary, file, indent=4)

        print("Project summary JSON exported")

        print("\nAll exports completed successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    export_project_data()
