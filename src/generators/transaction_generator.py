import random
import sqlite3
from datetime import datetime, timedelta
from faker import Faker

from config.settings import DATABASE_PATH, RANDOM_SEED, NUM_TRANSACTIONS

random.seed(RANDOM_SEED)
fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)

START_DATE = datetime(2025, 1, 1)
BATCH_SIZE = 5000


def generate_transactions():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    accounts = [
        row[0] for row in connection.execute(
            "SELECT account_id FROM account"
        )
    ]

    merchants = connection.execute("""
        SELECT merchant_id, merchant_name, primary_category_code
        FROM merchant
    """).fetchall()

    transactions = []
    ground_truth = []

    for i in range(1, NUM_TRANSACTIONS + 1):

        transaction_id = f"T{i:07d}"
        account_id = random.choice(accounts)

        transaction_date = START_DATE + timedelta(
            days=random.randint(0, 364)
        )

        if random.random() < 0.05:
            merchant_id = None
            category_code = "INCOME"
            description = random.choice([
                "SALARY CREDIT",
                "MONTHLY SALARY",
                "INTEREST CREDIT"
            ])
            transaction_type = "CREDIT"
            amount = round(random.uniform(10000, 80000), 2)

        else:
            merchant_id, merchant_name, category_code = random.choice(
                merchants
            )

            description = random.choice([
                merchant_name,
                f"{merchant_name} PAYMENT",
                f"UPI {merchant_name}",
                f"POS PURCHASE {merchant_name}"
            ])

            transaction_type = "DEBIT"
            amount = round(random.uniform(50, 10000), 2)

        status = random.choices(
            ["COMPLETED", "PENDING", "FAILED", "REVERSED"],
            weights=[94, 3, 2, 1]
        )[0]

        payment_method = random.choice([
            "UPI", "CARD", "NET_BANKING", "CASH"
        ])

        created_at = transaction_date.isoformat()

        transactions.append((
            transaction_id,
            account_id,
            merchant_id,
            None,
            transaction_date.date().isoformat(),
            description,
            amount,
            transaction_type,
            payment_method,
            "INR",
            status,
            created_at
        ))

        ground_truth.append((
            f"GT{i:07d}",
            transaction_id,
            category_code,
            "SYNTHETIC_GENERATOR",
            created_at
        ))

        if len(transactions) >= BATCH_SIZE:
            connection.executemany("""
                INSERT INTO transactions VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, transactions)

            connection.executemany("""
                INSERT INTO transaction_category_ground_truth
                VALUES (?, ?, ?, ?, ?)
            """, ground_truth)

            connection.commit()
            transactions.clear()
            ground_truth.clear()

            if i % 50000 == 0:
                print(f"Generated {i:,} transactions")

    if transactions:
        connection.executemany(
            "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            transactions
        )

        connection.executemany(
            "INSERT INTO transaction_category_ground_truth VALUES (?, ?, ?, ?, ?)",
            ground_truth
        )

        connection.commit()

    connection.close()
    print(f"Completed: {NUM_TRANSACTIONS:,} transactions generated!")


if __name__ == "__main__":
    generate_transactions()