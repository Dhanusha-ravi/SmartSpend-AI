
import random
import sqlite3
from datetime import datetime, timedelta
from faker import Faker

from config.test_settings import DATABASE_PATH, RANDOM_SEED, NUM_USERS

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


def generate_users():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        users = []
        accounts = []

        base_date = datetime(2025, 1, 1)

        for i in range(1, NUM_USERS + 1):
            user_id = f"U{i:06d}"
            account_id = f"ACC{i:06d}"

            created_at = (
                base_date + timedelta(days=random.randint(0, 365))
            ).isoformat()

            users.append((
                user_id,
                fake.first_name(),
                fake.last_name(),
                f"user{i}@example.com",
                fake.phone_number(),
                fake.city(),
                fake.state(),
                "India",
                created_at,
                "ACTIVE"
            ))

            accounts.append((
                account_id,
                user_id,
                random.choice(["SAVINGS", "CURRENT", "CREDIT"]),
                fake.company(),
                "INR",
                round(random.uniform(5000, 200000), 2),
                created_at[:10],
                "ACTIVE"
            ))

        connection.execute("PRAGMA foreign_keys = ON")

        connection.executemany("""
            INSERT INTO user_profile
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, users)

        connection.executemany("""
            INSERT INTO account
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, accounts)

        connection.commit()

        print(f"Users generated: {len(users)}")
        print(f"Accounts generated: {len(accounts)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_users()
