
import sqlite3
import random

from config.test_settings import DATABASE_PATH, RANDOM_SEED


BUDGET_CATEGORIES = [
    "EDUCATION",
    "ENTERTAINMENT",
    "FOOD",
    "GROCERY",
    "HEALTH",
    "HOUSING",
    "SHOPPING",
    "TRANSPORT",
    "UTILITIES",
]

FALLBACK_BUDGETS = {
    "EDUCATION": 3000,
    "ENTERTAINMENT": 2500,
    "FOOD": 5000,
    "GROCERY": 6000,
    "HEALTH": 3000,
    "HOUSING": 10000,
    "SHOPPING": 4000,
    "TRANSPORT": 3000,
    "UTILITIES": 2500,
}


def generate_budgets():
    random.seed(RANDOM_SEED)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = connection.cursor()

        users = cursor.execute(
            "SELECT user_id FROM user_profile ORDER BY user_id"
        ).fetchall()

        categories = cursor.execute(
            "SELECT category_code FROM category"
        ).fetchall()

        valid_categories = {
            row[0] for row in categories
        }

        selected_categories = [
            category
            for category in BUDGET_CATEGORIES
            if category in valid_categories
        ]

        if not selected_categories:
            raise ValueError("No valid budget categories found.")

        spending_rows = cursor.execute(
            """
            SELECT
                t.account_id,
                g.actual_category_code,
                SUM(t.amount) / 12.0
            FROM transactions t
            JOIN transaction_category_ground_truth g
                ON t.transaction_id = g.transaction_id
            WHERE t.transaction_type = 'DEBIT'
              AND t.status = 'COMPLETED'
              AND t.transaction_date >= '2025-01-01'
              AND t.transaction_date < '2026-01-01'
              AND g.actual_category_code IN (
                  SELECT category_code FROM category
              )
            GROUP BY
                t.account_id,
                g.actual_category_code
            """
        ).fetchall()

        account_users = cursor.execute(
            "SELECT account_id, user_id FROM account"
        ).fetchall()

        account_to_user = {
            account_id: user_id
            for account_id, user_id in account_users
        }

        average_spending = {}

        for account_id, category, amount in spending_rows:
            user_id = account_to_user.get(account_id)

            if user_id is None or category not in selected_categories:
                continue

            key = (user_id, category)

            average_spending[key] = (
                average_spending.get(key, 0) + float(amount)
            )

        existing_rows = cursor.execute(
            """
            SELECT user_id, category_code, start_date
            FROM budget
            """
        ).fetchall()

        existing_keys = set(existing_rows)

        new_records = 0

        for user_row in users:
            user_id = user_row[0]

            for category in selected_categories:
                average = average_spending.get(
                    (user_id, category), 0
                )

                base_amount = (
                    average
                    if average > 0
                    else FALLBACK_BUDGETS[category]
                )

                for month in range(1, 13):
                    start_date = f"2025-{month:02d}-01"

                    if (user_id, category, start_date) in existing_keys:
                        continue

                    budget_amount = round(
                        base_amount * random.uniform(0.85, 1.15),
                        2
                    )

                    last_day = (
                        31 if month in [1, 3, 5, 7, 8, 10, 12]
                        else 30 if month in [4, 6, 9, 11]
                        else 28
                    )

                    end_date = (
                        f"2025-{month:02d}-{last_day:02d}"
                    )

                    budget_id = (
                        f"BUD-{user_id}-{category}-{month:02d}"
                    )

                    cursor.execute(
                        """
                        INSERT INTO budget (
                            budget_id,
                            user_id,
                            category_code,
                            budget_amount,
                            budget_period,
                            start_date,
                            end_date
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            budget_id,
                            user_id,
                            category,
                            budget_amount,
                            "MONTHLY",
                            start_date,
                            end_date,
                        )
                    )

                    existing_keys.add(
                        (user_id, category, start_date)
                    )

                    new_records += 1

        connection.commit()

        print("Budget generation completed.")
        print(f"Users: {len(users)}")
        print(f"Categories: {len(selected_categories)}")
        print(f"New budget records: {new_records}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_budgets()
