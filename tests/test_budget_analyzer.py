import pytest

from src.analytics.budget_analyzer import analyze_monthly_budget


def test_invalid_month_zero():
    with pytest.raises(ValueError):
        analyze_monthly_budget("U000001", 2025, 0)


def test_invalid_month_thirteen():
    with pytest.raises(ValueError):
        analyze_monthly_budget("U000001", 2025, 13)


def test_budget_report_returns_categories():
    results = analyze_monthly_budget("U000001", 2025, 1)

    assert len(results) == 9


def test_budget_report_has_required_fields():
    results = analyze_monthly_budget("U000001", 2025, 1)

    required_fields = {
        "category",
        "budget",
        "spent",
        "remaining",
        "utilization_percent",
        "status"
    }

    for result in results:
        assert required_fields.issubset(result.keys())


def test_budget_status_is_valid():
    results = analyze_monthly_budget("U000001", 2025, 1)

    valid_statuses = {
        "OVER_BUDGET",
        "NEAR_LIMIT",
        "WITHIN_BUDGET"
    }

    for result in results:
        assert result["status"] in valid_statuses


def test_remaining_amount_calculation():
    results = analyze_monthly_budget("U000001", 2025, 1)

    for result in results:
        expected_remaining = round(
            result["budget"] - result["spent"], 2
        )

        assert result["remaining"] == expected_remaining