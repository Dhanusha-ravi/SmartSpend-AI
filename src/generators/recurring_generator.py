import random
import sqlite3

from config.settings import DATABASE_PATH, RANDOM_SEED

random.seed(RANDOM_SEED)

RECURRING_PAYMENTS = [
    ("Netflix Subscription", "M009", "ENTERTAINMENT", 649, "MONTHLY"),
    ("Spotify Subscription", "M010", "ENTERTAINMENT", 119, "MONTHLY"),
    ("Mobile Recharge", "M011", "UTILITIES", 299, "MONTHLY"),
    ("Electricity Bill", "M012", "UTILITIES", 1200, "MONTHLY"),
    ("House Rent", "M017", "HOUSING", 12000, "MONTHLY"),
    ("Insurance Premium", "M018", "FINANCE", 5000, "YEARLY")
]


def generate_recurring():
    connection = sqlite3.connect(DATABASE_PATH)

    users = connection.execute(
        "SELECT user_id FROM user_profile"
    ).fetchall()

    recurring_records = []
    record_number = 1

    for user in users:
        user_id = user[0]

        selected_payments = random.sample(
            RECURRING_PAYMENTS,
            random.randint(1, 3)
        )

        for name, merchant_id, category, amount, frequency in selected_payments:

            recurring_records.append((
                f"RCP{record_number:06d}",
                user_id,
                merchant_id,
                category,
                name,
                amount,
                frequency,
                "2025-01-01",
                "2025-12-01",
                "ACTIVE",
                round(random.uniform(0.85, 0.99), 2)
            ))

            record_number += 1

    connection.executemany("""
        INSERT OR IGNORE INTO recurring_series
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, recurring_records)

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM recurring_series"
    ).fetchone()[0]

    print("Recurring payment records:", count)

    connection.close()


if __name__ == "__main__":
    generate_recurring()