
import pytest

from src.business_logic.anomaly_handler import handle_anomaly


def test_transfer_excluded_from_expenses():
    result = handle_anomaly("TRANSFER_DOUBLE_COUNT")

    assert result["decision"] == "EXCLUDE_FROM_EXPENSE_TOTAL"
    assert result["include_in_expense"] is False


def test_refund_treated_as_credit():
    result = handle_anomaly("REFUND_AS_NEW_EXPENSE")

    assert result["decision"] == "TREAT_AS_REFUND_CREDIT"
    assert result["include_in_expense"] is False
    assert result["adjusts_expense_total"] is True


def test_missing_recurring_payment_flagged():
    result = handle_anomaly("RECURRING_PAYMENT_SKIPPED")

    assert result["decision"] == "FLAG_MISSING_RECURRING_PAYMENT"
    assert result["status"] == "REVIEW"


def test_timezone_boundary_normalized_to_utc():
    result = handle_anomaly(
        "TIMEZONE_BOUNDARY",
        transaction={
            "transaction_date": "2025-12-31T23:30:00-05:00"
        },
    )

    assert result["decision"] == "NORMALIZE_TO_UTC_DATE"
    assert result["normalized_date"] == "2026-01-01"


def test_invalid_budget_category_rejected():
    result = handle_anomaly(
        "INVALID_BUDGET_CATEGORY",
        transaction={"category_code": "UNKNOWN"},
        valid_categories={"FOOD", "SHOPPING"},
    )

    assert result["decision"] == "REJECT_INVALID_CATEGORY"
    assert result["valid"] is False


def test_valid_budget_category_accepted():
    result = handle_anomaly(
        "INVALID_BUDGET_CATEGORY",
        transaction={"category_code": "FOOD"},
        valid_categories={"FOOD", "SHOPPING"},
    )

    assert result["decision"] == "ACCEPT_VALID_CATEGORY"
    assert result["valid"] is True


def test_timezone_requires_timezone_information():
    with pytest.raises(ValueError):
        handle_anomaly(
            "TIMEZONE_BOUNDARY",
            transaction={
                "transaction_date": "2025-12-31T23:30:00"
            },
        )


def test_unknown_anomaly_rejected():
    with pytest.raises(ValueError):
        handle_anomaly("UNKNOWN_SCENARIO")
