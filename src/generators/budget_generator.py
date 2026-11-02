import random
import sqlite3

from config.settings import DATABASE_PATH, RANDOM_SEED

random.seed(RANDOM_SEED)

FALLBACK_BUDGETS = {
    "FOOD": 5000,
    "GROCERY": 4000,
    "TRANSPORT": 3000,
    "SHOPPING": 5000,
    "ENTERTAINMENT": 2000,
    "UTILITIES": 2500,
    "HEALTH": 2000,
    "EDUCATION": 3000,
    "HOUSING": 10000
}


def generate_budgets():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        spending_data = connection.execute("""
            SELECT
                a.user_id,
                t.category_code,
                SUM(t.amount) / 12.0 AS average_monthly_spending
            FROM transactions t
            JOIN account a ON t.account_id = a.account_id
            WHERE t.transaction_type = 'DEBIT'
              AND t.status = 'COMPLETED'
              AND t.category_code IS NOT NULL
              AND t.transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
            GROUP BY a.user_id, t.category_code
        """).fetchall()

        spending_lookup = {
            (user_id, category): average
            for user_id, category, average in spending_data
        }

        budgets = connection.execute("""
            SELECT budget_id, user_id, category_code
            FROM budget
        """).fetchall()

        updates = []

        for budget_id, user_id, category in budgets:
            average_spending = spending_lookup.get(
                (user_id, category), 0
            )

            if average_spending > 0:
                budget_amount = average_spending * random.uniform(
                    0.85, 1.15
                )
            else:
                budget_amount = FALLBACK_BUDGETS[category]

            updates.append((
                round(budget_amount, 2),
                budget_id
            ))

        connection.executemany("""
            UPDATE budget
            SET budget_amount = ?
            WHERE budget_id = ?
        """, updates)

        connection.commit()

        print("Budget records updated:", len(updates))

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_budgets()