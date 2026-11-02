import sqlite3
import calendar

from config.settings import DATABASE_PATH


def analyze_monthly_budget(user_id, year, month):
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")

    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    query = """
        SELECT
            b.category_code,
            b.budget_amount,
            COALESCE(SUM(t.amount), 0) AS actual_spending
        FROM budget b
        LEFT JOIN account a
            ON a.user_id = b.user_id
        LEFT JOIN transactions t
            ON t.account_id = a.account_id
            AND t.category_code = b.category_code
            AND t.transaction_type = 'DEBIT'
            AND t.status = 'COMPLETED'
            AND t.transaction_date BETWEEN ? AND ?
        WHERE b.user_id = ?
          AND b.budget_period = 'MONTHLY'
          AND b.start_date <= ?
          AND b.end_date >= ?
        GROUP BY b.category_code, b.budget_amount
        ORDER BY b.category_code
    """

    try:
        rows = connection.execute(
            query,
            (start_date, end_date, user_id, end_date, start_date)
        ).fetchall()

        results = []

        for row in rows:
            budget = float(row["budget_amount"])
            spent = float(row["actual_spending"])
            remaining = budget - spent
            utilization = (spent / budget * 100) if budget > 0 else 0

            if spent > budget:
                status = "OVER_BUDGET"
            elif utilization >= 80:
                status = "NEAR_LIMIT"
            else:
                status = "WITHIN_BUDGET"

            results.append({
                "category": row["category_code"],
                "budget": round(budget, 2),
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "utilization_percent": round(utilization, 2),
                "status": status
            })

        return results

    finally:
        connection.close()


if __name__ == "__main__":
    report = analyze_monthly_budget("U000001", 2025, 1)

    print("MONTHLY BUDGET REPORT")
    print("=" * 60)

    for item in report:
        print(item)