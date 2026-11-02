import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH
from src.business_logic.recurring_detector import (
    get_recurring_series,
    analyze_recurring_series
)


def save_test_matches():
    series = get_recurring_series()[0]
    results = analyze_recurring_series(series)

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        saved_count = 0

        for result in results:
            if result["match_status"] != "MATCHED":
                continue

            connection.execute("""
                INSERT OR IGNORE INTO transaction_recurring_match (
                    match_id,
                    transaction_id,
                    recurring_id,
                    match_confidence,
                    match_status,
                    matched_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"MATCH_{result['transaction_id']}",
                result["transaction_id"],
                series["recurring_id"],
                result["match_confidence"],
                result["match_status"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            if connection.execute("SELECT changes()").fetchone()[0]:
                saved_count += 1

        connection.commit()
        print("New matches saved:", saved_count)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    save_test_matches()
