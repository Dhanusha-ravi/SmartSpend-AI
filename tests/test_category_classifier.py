from src.business_logic.category_classifier import classify_transaction


def test_income_classification():
    category, confidence = classify_transaction(
        "Monthly salary",
        None,
        None,
        "CREDIT",
        []
    )

    assert category == "INCOME"
    assert confidence == 0.99


def test_merchant_rule_classification():
    rules = [{
        "merchant_pattern": "SWIGGY",
        "description_pattern": None,
        "category_code": "FOOD",
        "confidence_score": 0.98
    }]

    category, confidence = classify_transaction(
        "Food order",
        "Swiggy",
        "FOOD",
        "DEBIT",
        rules
    )

    assert category == "FOOD"
    assert confidence == 0.98


def test_primary_category_fallback():
    category, confidence = classify_transaction(
        "Payment",
        "NoBroker",
        "HOUSING",
        "DEBIT",
        []
    )

    assert category == "HOUSING"
    assert confidence == 0.90


def test_other_fallback():
    category, confidence = classify_transaction(
        "Unknown payment",
        None,
        None,
        "DEBIT",
        []
    )

    assert category == "OTHER"
    assert confidence == 0.50


def test_merchant_matching_is_case_insensitive():
    rules = [{
        "merchant_pattern": "NETFLIX",
        "description_pattern": None,
        "category_code": "ENTERTAINMENT",
        "confidence_score": 0.99
    }]

    category, confidence = classify_transaction(
        "Subscription",
        "netflix",
        "ENTERTAINMENT",
        "DEBIT",
        rules
    )

    assert category == "ENTERTAINMENT"
    assert confidence == 0.99