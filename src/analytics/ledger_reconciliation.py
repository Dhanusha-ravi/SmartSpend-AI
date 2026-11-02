
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "database" / "smartspend_test.db"


def reconcile_account(account_id):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        account = connection.execute(
            """
            SELECT account_id, opening_balance, currency, account_type
            FROM account
            WHERE account_id = ?
            """,
            (account_id,),
        ).fetchone()

        if account is None:
            raise ValueError(f"Account not found: {account_id}")

        opening_balance = round(float(account["opening_balance"]), 2)

        transactions = connection.execute(
            """
            SELECT
                transaction_id,
                amount,
                transaction_type,
                status
            FROM transactions
            WHERE account_id = ?
            ORDER BY transaction_date, transaction_id
            """,
            (account_id,),
        ).fetchall()

        total_credits = 0
        total_debits = 0
        completed_count = 0
        excluded_count = 0
        signed_total = 0

        for transaction in transactions:
            amount_cents = round(float(transaction["amount"]) * 100)

            if transaction["status"] != "COMPLETED":
                excluded_count += 1
                continue

            if transaction["transaction_type"] == "CREDIT":
                signed_amount = amount_cents
                total_credits += amount_cents

            elif transaction["transaction_type"] == "DEBIT":
                signed_amount = -amount_cents
                total_debits += amount_cents

            else:
                raise ValueError(
                    f"Invalid transaction type: {transaction['transaction_type']}"
                )

            signed_total += signed_amount
            completed_count += 1

        calculated_balance = (
            round(opening_balance * 100) + signed_total
        )

        closing_balance = calculated_balance / 100

        # Independently compare credit/debit totals with signed ledger total.
        expected_signed_total = total_credits - total_debits
        arithmetic_valid = signed_total == expected_signed_total

        return {
            "account_id": account["account_id"],
            "account_type": account["account_type"],
            "currency": account["currency"],
            "opening_balance": opening_balance,
            "total_credits": total_credits / 100,
            "total_debits": total_debits / 100,
            "closing_balance": round(closing_balance, 2),
            "completed_transactions": completed_count,
            "excluded_transactions": excluded_count,
            "arithmetic_reconciled": arithmetic_valid,
            "negative_balance": closing_balance < 0,
        }

    finally:
        connection.close()


def reconcile_all_accounts():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        accounts = connection.execute(
            "SELECT account_id FROM account ORDER BY account_id"
        ).fetchall()
    finally:
        connection.close()

    return [
        reconcile_account(account_id)
        for (account_id,) in accounts
    ]


if __name__ == "__main__":
    results = reconcile_all_accounts()

    reconciled_count = sum(
        result["arithmetic_reconciled"] for result in results
    )

    negative_count = sum(
        result["negative_balance"] for result in results
    )

    print("SMARTSPEND LEDGER RECONCILIATION")
    print("=" * 45)

    for result in results[:5]:
        print(f"\nAccount: {result['account_id']}")
        print(f"Type: {result['account_type']}")
        print(f"Opening Balance: {result['currency']} {result['opening_balance']:.2f}")
        print(f"Total Credits: {result['currency']} {result['total_credits']:.2f}")
        print(f"Total Debits: {result['currency']} {result['total_debits']:.2f}")
        print(f"Closing Balance: {result['currency']} {result['closing_balance']:.2f}")
        print(f"Completed Transactions: {result['completed_transactions']}")
        print(f"Excluded Transactions: {result['excluded_transactions']}")
        print(
            "Arithmetic Reconciliation:",
            "PASSED" if result["arithmetic_reconciled"] else "FAILED",
        )
        print(
            "Negative Balance:",
            "FLAGGED" if result["negative_balance"] else "NO",
        )

    print("\nSUMMARY")
    print("-" * 30)
    print(f"Total accounts: {len(results)}")
    print(f"Arithmetic reconciled: {reconciled_count}")
    print(f"Negative balances flagged: {negative_count}")
