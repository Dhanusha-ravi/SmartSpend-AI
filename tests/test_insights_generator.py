from src.analytics.insights_generator import generate_spending_insights


def test_insights_return_list():
    results = generate_spending_insights("U000001", 2025, 1)
    assert isinstance(results, list)


def test_insights_not_empty():
    results = generate_spending_insights("U000001", 2025, 1)
    assert len(results) > 0


def test_highest_spending_category_is_first():
    results = generate_spending_insights("U000001", 2025, 1)
    assert results[0].startswith("Highest spending category:")


def test_total_spending_is_included():
    results = generate_spending_insights("U000001", 2025, 1)
    assert any("Total monthly spending:" in item for item in results)


def test_empty_user_returns_message():
    results = generate_spending_insights("UNKNOWN_USER", 2025, 1)
    assert results == [
        "No spending transactions found for this month."
    ]


def test_budget_alerts_are_generated():
    results = generate_spending_insights("U000001", 2025, 1)
    assert "BUDGET ALERTS" in results
    assert any("OVER BUDGET:" in item for item in results)


def test_invalid_month_zero():
    import pytest

    with pytest.raises(ValueError):
        generate_spending_insights("U000001", 2025, 0)


def test_invalid_month_thirteen():
    import pytest

    with pytest.raises(ValueError):
        generate_spending_insights("U000001", 2025, 13)