import sqlite3

from config.settings import DATABASE_PATH


def test_no_duplicate_transaction_ids():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute("""
        SELECT COUNT(*) FROM (
            SELECT transaction_id
            FROM transactions
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]

    connection.close()
    assert result == 0


def test_all_transactions_have_ground_truth():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute("""
        SELECT COUNT(*)
        FROM transactions t
        LEFT JOIN transaction_category_ground_truth g
        ON t.transaction_id = g.transaction_id
        WHERE g.transaction_id IS NULL
    """).fetchone()[0]

    connection.close()
    assert result == 0


def test_no_invalid_transaction_amounts():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE amount <= 0
    """).fetchone()[0]

    connection.close()
    assert result == 0


def test_no_missing_descriptions():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE description IS NULL OR TRIM(description) = ''
    """).fetchone()[0]

    connection.close()
    assert result == 0


def test_no_foreign_key_errors():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    connection.close()
    assert len(result) == 0


def test_all_transactions_have_categories():
    connection = sqlite3.connect(DATABASE_PATH)

    result = connection.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE category_code IS NULL
    """).fetchone()[0]

    connection.close()
    assert result == 0