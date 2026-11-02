
import sqlite3
import calendar

from config.test_settings import DATABASE_PATH


def generate_spending_insights(user_id, year, month):
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")

    start_date = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT
                COALESCE(
                    g.actual_category_code,
                    t.category_code,
                    'UNCATEGORIZED'
                ) AS category_code,

                SUM(
                    CASE
                        WHEN t.transaction_type = 'DEBIT'
                            THEN t.amount
                        WHEN t.transaction_type = 'CREDIT'
                            THEN -t.amount
                        ELSE 0
                    END
                ) AS total_spending,

                COUNT(*) AS transaction_count

            FROM transactions t

            LEFT JOIN transaction_category_ground_truth g
                ON t.transaction_id = g.transaction_id

            JOIN account a
                ON t.account_id = a.account_id

            LEFT JOIN anomaly_ground_truth ag
                ON t.transaction_id = ag.transaction_id
               AND ag.scenario_type = 'REFUND_AS_NEW_EXPENSE'

            WHERE a.user_id = ?
              AND t.status = 'COMPLETED'
              AND t.transaction_date BETWEEN ? AND ?

              AND (
                    (
                        t.transaction_type = 'DEBIT'
                        AND COALESCE(
                            t.category_code,
                            g.actual_category_code,
                            ''
                        ) != 'TRANSFER'
                    )
                    OR
                    (
                        t.transaction_type = 'CREDIT'
                        AND ag.scenario_type = 'REFUND_AS_NEW_EXPENSE'
                    )
              )

            GROUP BY COALESCE(
                g.actual_category_code,
                t.category_code,
                'UNCATEGORIZED'
            )

            ORDER BY total_spending DESC

        """, (user_id, start_date, end_date)).fetchall()

        if not rows:
            return ["No spending transactions found for this month."]

        insights = []

        spending_rows = [
            row for row in rows
            if float(row["total_spending"]) > 0
        ]

        if not spending_rows:
            return ["No positive net spending found for this month."]

        highest = spending_rows[0]

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

        insights.append("CATEGORY-WISE NET SPENDING")

        for row in rows:
            insights.append(
                f"{row['category_code']}: "
                f"{row['transaction_count']} transactions, "
                f"₹{row['total_spending']:.2f}"
            )

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

        insights.append("BUDGET ALERTS")

        alert_found = False

        for row in spending_rows:
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
        11
    )

    print("SMARTSPEND MONTHLY INSIGHTS")
    print("=" * 45)

    for insight in results:
        print("-", insight)
