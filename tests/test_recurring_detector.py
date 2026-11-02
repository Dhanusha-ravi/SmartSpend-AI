from src.business_logic.recurring_detector import (
    calculate_amount_confidence,
    calculate_date_confidence,
    calculate_match_confidence,
    determine_match_status,
    group_transactions_by_period,
    select_best_transaction,
)


def test_exact_amount_match():
    assert calculate_amount_confidence(649, 649) == 1.0


def test_amount_mismatch():
    assert calculate_amount_confidence(2000, 649) == 0.0


def test_monthly_date_match():
    assert calculate_date_confidence(
        "2025-01-05", "2025-02-05", "MONTHLY"
    ) == 1.0


def test_yearly_date_match():
    assert calculate_date_confidence(
        "2025-01-05", "2026-01-05", "YEARLY"
    ) == 1.0


def test_invalid_date_sequence():
    assert calculate_date_confidence(
        "2025-02-05", "2025-01-05", "MONTHLY"
    ) == 0.0


def test_match_confidence():
    assert calculate_match_confidence(1.0, 1.0) == 1.0


def test_match_status():
    assert determine_match_status(1.0) == "MATCHED"
    assert determine_match_status(0.7) == "REVIEW"
    assert determine_match_status(0.3) == "REJECTED"


def test_group_transactions_by_month():
    transactions = [
        {"transaction_date": "2025-01-05", "amount": 649},
        {"transaction_date": "2025-01-20", "amount": 700},
        {"transaction_date": "2025-02-05", "amount": 649},
    ]

    result = group_transactions_by_period(transactions, "MONTHLY")

    assert len(result["2025-01"]) == 2
    assert len(result["2025-02"]) == 1


def test_select_best_transaction():
    grouped = {
        "2025-01": [
            {"transaction_id": "T1", "amount": 900},
            {"transaction_id": "T2", "amount": 649},
            {"transaction_id": "T3", "amount": 700},
        ]
    }

    result = select_best_transaction(grouped, 649)

    assert result[0]["transaction_id"] == "T2"