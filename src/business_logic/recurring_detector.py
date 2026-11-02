
import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH


# 1. Load active recurring payment series
def get_recurring_series():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    query = """
        SELECT
            recurring_id,
            user_id,
            merchant_id,
            recurring_name,
            expected_amount,
            frequency
        FROM recurring_series
        WHERE status = 'ACTIVE'
    """

    recurring_series = connection.execute(query).fetchall()
    connection.close()

    return recurring_series


# 2. Get transactions for a user and merchant
def get_candidate_transactions(user_id, merchant_id):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    query = """
        SELECT
            t.transaction_id,
            t.transaction_date,
            t.amount,
            t.description
        FROM transactions t
        JOIN account a
            ON t.account_id = a.account_id
        WHERE a.user_id = ?
          AND t.merchant_id = ?
          AND t.transaction_type = 'DEBIT'
          AND t.status = 'COMPLETED'
        ORDER BY t.transaction_date
    """

    transactions = connection.execute(
        query,
        (user_id, merchant_id)
    ).fetchall()

    connection.close()

    return transactions


# 3. Calculate amount confidence
def calculate_amount_confidence(actual_amount, expected_amount):
    if expected_amount <= 0:
        return 0.0

    difference = abs(actual_amount - expected_amount)
    percentage_difference = difference / expected_amount

    if percentage_difference <= 0.10:
        return 1.0
    elif percentage_difference <= 0.20:
        return 0.8
    elif percentage_difference <= 0.30:
        return 0.5

    return 0.0


# 4. Calculate date confidence
def calculate_date_confidence(previous_date, current_date, frequency):
    previous = datetime.strptime(previous_date, "%Y-%m-%d")
    current = datetime.strptime(current_date, "%Y-%m-%d")

    if current <= previous:
        return 0.0

    if frequency == "MONTHLY":
        month_difference = (
            (current.year - previous.year) * 12
            + current.month - previous.month
        )

        if month_difference == 1:
            return 1.0

    elif frequency == "YEARLY":
        year_difference = current.year - previous.year

        if year_difference == 1 and current.month == previous.month:
            return 1.0

    return 0.0


# 5. Calculate overall match confidence
def calculate_match_confidence(amount_confidence, date_confidence):
    confidence = (
        amount_confidence * 0.6
        + date_confidence * 0.4
    )

    return round(confidence, 2)


# 6. Determine matching status
def determine_match_status(confidence):
    if confidence >= 0.85:
        return "MATCHED"
    elif confidence >= 0.60:
        return "REVIEW"

    return "REJECTED"


# 7. Group transactions by month or year
def group_transactions_by_period(transactions, frequency):
    grouped_transactions = {}

    for transaction in transactions:
        transaction_date = datetime.strptime(
            transaction["transaction_date"],
            "%Y-%m-%d"
        )

        if frequency == "MONTHLY":
            period = transaction_date.strftime("%Y-%m")

        elif frequency == "YEARLY":
            period = transaction_date.strftime("%Y")

        else:
            continue

        if period not in grouped_transactions:
            grouped_transactions[period] = []

        grouped_transactions[period].append(transaction)

    return grouped_transactions


# 8. Select the best transaction in each period
def select_best_transaction(grouped_transactions, expected_amount):
    selected_transactions = []

    for period in sorted(grouped_transactions):
        candidates = grouped_transactions[period]

        best_transaction = min(
            candidates,
            key=lambda transaction: abs(
                transaction["amount"] - expected_amount
            )
        )

        selected_transactions.append(best_transaction)

    return selected_transactions


# 9. Evaluate two consecutive recurring transactions
def evaluate_transaction_pair(
    previous_transaction,
    current_transaction,
    expected_amount,
    frequency
):
    amount_confidence = calculate_amount_confidence(
        current_transaction["amount"],
        expected_amount
    )

    date_confidence = calculate_date_confidence(
        previous_transaction["transaction_date"],
        current_transaction["transaction_date"],
        frequency
    )

    confidence = calculate_match_confidence(
        amount_confidence,
        date_confidence
    )

    status = determine_match_status(confidence)

    return {
        "transaction_id": current_transaction["transaction_id"],
        "match_confidence": confidence,
        "match_status": status
    }


# 10. Analyze one recurring payment series
def analyze_recurring_series(series):
    transactions = get_candidate_transactions(
        series["user_id"],
        series["merchant_id"]
    )

    if not transactions:
        return []

    grouped_transactions = group_transactions_by_period(
        transactions,
        series["frequency"]
    )

    selected_transactions = select_best_transaction(
        grouped_transactions,
        series["expected_amount"]
    )

    results = []

    for index in range(1, len(selected_transactions)):
        previous_transaction = selected_transactions[index - 1]
        current_transaction = selected_transactions[index]

        result = evaluate_transaction_pair(
            previous_transaction,
            current_transaction,
            series["expected_amount"],
            series["frequency"]
        )

        results.append(result)

    return results
