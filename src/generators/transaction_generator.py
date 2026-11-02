
import random
import sqlite3
from datetime import datetime, timedelta
from faker import Faker

from config.test_settings import DATABASE_PATH, RANDOM_SEED, NUM_TRANSACTIONS

random.seed(RANDOM_SEED)
fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)

START_DATE = datetime(2025, 1, 1)
BATCH_SIZE = 5000

SALARY_MIN = 30000
SALARY_MAX = 80000


def generate_transactions():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        accounts = [
            row[0] for row in connection.execute(
                "SELECT account_id FROM account ORDER BY account_id"
            )
        ]

        if not accounts:
            raise ValueError("No accounts found. Generate users first.")

        merchants = connection.execute("""
            SELECT merchant_id, merchant_name, primary_category_code
            FROM merchant
        """).fetchall()

        if not merchants:
            raise ValueError("No merchants found. Seed merchant data first.")

        transactions = []
        ground_truth = []

        def save_batch():
            if not transactions:
                return

            connection.executemany("""
                INSERT INTO transactions (
                    transaction_id, account_id, merchant_id,
                    category_code, transaction_date, description,
                    amount, transaction_type, payment_method,
                    currency, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, transactions)

            connection.executemany("""
                INSERT INTO transaction_category_ground_truth (
                    ground_truth_id, transaction_id,
                    actual_category_code, verified_by, verified_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, ground_truth)

            connection.commit()
            transactions.clear()
            ground_truth.clear()

        # Generate monthly salary credits for every account.
        salary_count = 0

        for account_id in accounts:
            for month in range(1, 13):
                salary_date = datetime(2025, month, 1) + timedelta(days=4)
                transaction_id = f"SAL-{account_id}-{month:02d}"
                created_at = salary_date.isoformat()
                amount = round(
                    random.uniform(SALARY_MIN, SALARY_MAX), 2
                )

                transactions.append((
                    transaction_id,
                    account_id,
                    None,
                    None,
                    salary_date.date().isoformat(),
                    "MONTHLY SALARY CREDIT",
                    amount,
                    "CREDIT",
                    "BANK_TRANSFER",
                    "INR",
                    "COMPLETED",
                    created_at
                ))

                ground_truth.append((
                    f"GT-{transaction_id}",
                    transaction_id,
                    "INCOME",
                    "SYNTHETIC_GENERATOR",
                    created_at
                ))

                salary_count += 1

                if len(transactions) >= BATCH_SIZE:
                    save_batch()

        # Generate regular transactions.
        for i in range(1, NUM_TRANSACTIONS + 1):
            transaction_id = f"T{i:07d}"
            account_id = random.choice(accounts)

            transaction_date = START_DATE + timedelta(
                days=random.randint(0, 364)
            )

            merchant_id, merchant_name, category_code = random.choice(
                merchants
            )

            description = random.choice([
                merchant_name,
                f"{merchant_name} PAYMENT",
                f"UPI {merchant_name}",
                f"POS PURCHASE {merchant_name}"
            ])

            amount = round(random.uniform(50, 2500), 2)

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
                "DEBIT",
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
                save_batch()

            if i % 50000 == 0:
                print(f"Generated {i:,} regular transactions")

        save_batch()

        print("\nTransaction generation completed!")
        print(f"Regular transactions: {NUM_TRANSACTIONS:,}")
        print(f"Monthly salary transactions: {salary_count:,}")
        print(
            f"Total generated: {NUM_TRANSACTIONS + salary_count:,}"
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_transactions()
