import sqlite3
import calendar

from config.settings import DATABASE_PATH


def generate_spending_insights(user_id, year, month):
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")

    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        # 1. Get monthly category-wise spending
        rows = connection.execute("""
            SELECT
                t.category_code,
                SUM(t.amount) AS total_spending,
                COUNT(*) AS transaction_count
            FROM transactions t
            JOIN account a
                ON t.account_id = a.account_id
            WHERE a.user_id = ?
              AND t.transaction_type = 'DEBIT'
              AND t.status = 'COMPLETED'
              AND t.transaction_date BETWEEN ? AND ?
            GROUP BY t.category_code
            ORDER BY total_spending DESC
        """, (user_id, start_date, end_date)).fetchall()

        if not rows:
            return ["No spending transactions found for this month."]

        insights = []

        # 2. Calculate total spending
        highest = rows[0]

        total_spending = sum(
            float(row["total_spending"])
            for row in rows
        )

        insights.append(
            f"Highest spending category: "
            f"{highest['category_code']} "
            f"(₹{highest['total_spending']:.2f})"
        )

        insights.append(
            f"Total monthly spending: ₹{total_spending:.2f}"
        )

        # 3. Add category-wise spending details
        insights.append("CATEGORY-WISE SPENDING")

        for row in rows:
            insights.append(
                f"{row['category_code']}: "
                f"{row['transaction_count']} transactions, "
                f"₹{row['total_spending']:.2f}"
            )

        # 4. Get monthly budgets
        budgets = connection.execute("""
            SELECT
                category_code,
                budget_amount
            FROM budget
            WHERE user_id = ?
              AND budget_period = 'MONTHLY'
              AND start_date <= ?
              AND end_date >= ?
        """, (user_id, end_date, start_date)).fetchall()

        budget_lookup = {
            row["category_code"]: float(row["budget_amount"])
            for row in budgets
        }

        # 5. Generate budget alerts
        insights.append("BUDGET ALERTS")

        alert_found = False

        for row in rows:
            category = row["category_code"]
            spent = float(row["total_spending"])

            budget = budget_lookup.get(category)

            if budget is None or budget <= 0:
                continue

            utilization = (spent / budget) * 100

            if utilization > 100:
                insights.append(
                    f"OVER BUDGET: {category} is at "
                    f"{utilization:.2f}% of its budget."
                )
                alert_found = True

            elif utilization >= 80:
                insights.append(
                    f"NEAR LIMIT: {category} has used "
                    f"{utilization:.2f}% of its budget."
                )
                alert_found = True

        if not alert_found:
            insights.append(
                "No budget alerts. Spending is within limits."
            )

        return insights

    finally:
        connection.close()


if __name__ == "__main__":
    results = generate_spending_insights(
        "U000001",
        2025,
        1
    )

    print("SMARTSPEND MONTHLY INSIGHTS")
    print("=" * 45)

    for insight in results:
        print("-", insight)
