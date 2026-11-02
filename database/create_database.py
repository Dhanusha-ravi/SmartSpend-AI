
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

schema_file = BASE_DIR / "schema.sql"
seed_file = BASE_DIR / "seed_data.sql"
anomaly_schema_file = BASE_DIR / "anomaly_schema.sql"
database_file = BASE_DIR / "smartspend_test.db"

connection = sqlite3.connect(database_file)

try:
    connection.execute("PRAGMA foreign_keys = ON")

    with open(schema_file, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    with open(anomaly_schema_file, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    with open(seed_file, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    print("TEST database setup completed!")

    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

    print("\nTables:")
    for table in tables:
        print("-", table[0])

    categories = connection.execute("""
        SELECT category_code, category_name
        FROM category
        ORDER BY category_code
    """).fetchall()

    print("\nCategories inserted:", len(categories))

except sqlite3.Error as error:
    print("Database error:", error)
    raise

finally:
    connection.close()
