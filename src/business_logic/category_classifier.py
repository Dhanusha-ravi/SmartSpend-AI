import sqlite3

from config.settings import DATABASE_PATH


def classify_transaction(
    description,
    merchant_name,
    primary_category,
    transaction_type,
    rules
):
    # 1. Identify income transactions
    if transaction_type == "CREDIT":
        return "INCOME", 0.99

    # 2. Prepare transaction text
    text = f"{merchant_name or ''} {description or ''}".upper()

    # 3. Apply category rules based on priority
    for rule in rules:
        merchant_pattern = (rule["merchant_pattern"] or "").upper()
        description_pattern = (rule["description_pattern"] or "").upper()

        merchant_match = (
            merchant_pattern and merchant_pattern in text
        )

        description_match = (
            description_pattern and description_pattern in text
        )

        if merchant_match or description_match:
            return (
                rule["category_code"],
                rule["confidence_score"]
            )

    # 4. Use merchant's primary category as fallback
    if primary_category:
        return primary_category, 0.90

    # 5. Final fallback
    return "OTHER", 0.50


def classify_all_transactions():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Load active category rules
    rules = connection.execute("""
        SELECT
            merchant_pattern,
            description_pattern,
            category_code,
            confidence_score
        FROM category_rule
        WHERE is_active = 1
        ORDER BY priority DESC
    """).fetchall()

    # Load transactions and merchant details
    transactions = connection.execute("""
        SELECT
            t.transaction_id,
            t.description,
            t.transaction_type,
            m.merchant_name,
            m.primary_category_code
        FROM transactions t
        LEFT JOIN merchant m
            ON t.merchant_id = m.merchant_id
    """).fetchall()

    results = []

    # Classify every transaction
    for transaction in transactions:

        category, confidence = classify_transaction(
            transaction["description"],
            transaction["merchant_name"],
            transaction["primary_category_code"],
            transaction["transaction_type"],
            rules
        )

        results.append((
            category,
            transaction["transaction_id"]
        ))

    # Update predicted categories
    connection.executemany("""
        UPDATE transactions
        SET category_code = ?
        WHERE transaction_id = ?
    """, results)

    connection.commit()

    print("\nSMARTSPEND CLASSIFICATION RESULTS")
    print("=" * 40)

    print("Transactions classified:", len(results))

    print("\nCATEGORY DISTRIBUTION:")

    distribution = connection.execute("""
        SELECT
            category_code,
            COUNT(*)
        FROM transactions
        GROUP BY category_code
        ORDER BY COUNT(*) DESC
    """).fetchall()

    for row in distribution:
        print(f"{row[0]}: {row[1]}")

    connection.close()


if __name__ == "__main__":
    classify_all_transactions()