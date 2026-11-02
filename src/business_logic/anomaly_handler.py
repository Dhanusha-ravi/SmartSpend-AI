
from datetime import datetime, timezone


def handle_anomaly(
    scenario_type,
    transaction=None,
    valid_categories=None,
):
    """
    Apply a business decision for one of the five anomaly scenarios.
    Returns the decision and any derived values.
    """

    transaction = transaction or {}

    if scenario_type == "TRANSFER_DOUBLE_COUNT":
        return {
            "decision": "EXCLUDE_FROM_EXPENSE_TOTAL",
            "include_in_expense": False,
            "reason": "Internal transfers must not be counted as expenses.",
        }

    elif scenario_type == "REFUND_AS_NEW_EXPENSE":
        return {
            "decision": "TREAT_AS_REFUND_CREDIT",
            "include_in_expense": False,
            "adjusts_expense_total": True,
            "reason": "A refund offsets spending instead of creating a new expense.",
        }

    elif scenario_type == "RECURRING_PAYMENT_SKIPPED":
        return {
            "decision": "FLAG_MISSING_RECURRING_PAYMENT",
            "status": "REVIEW",
            "reason": "A missing expected recurring payment needs review.",
        }

    elif scenario_type == "TIMEZONE_BOUNDARY":
        transaction_date = transaction.get("transaction_date")

        if not transaction_date:
            raise ValueError("transaction_date is required.")

        parsed_date = datetime.fromisoformat(
            transaction_date.replace("Z", "+00:00")
        )

        if parsed_date.tzinfo is None:
            raise ValueError(
                "Timezone information is required for normalization."
            )

        utc_date = parsed_date.astimezone(timezone.utc).date().isoformat()

        return {
            "decision": "NORMALIZE_TO_UTC_DATE",
            "normalized_date": utc_date,
            "reason": "Transaction date converted to its UTC calendar date.",
        }

    elif scenario_type == "INVALID_BUDGET_CATEGORY":
        category = transaction.get("category_code")

        if valid_categories is None:
            raise ValueError("valid_categories must be provided.")

        if category not in valid_categories:
            return {
                "decision": "REJECT_INVALID_CATEGORY",
                "valid": False,
                "reason": f"Unknown budget category: {category}",
            }

        return {
            "decision": "ACCEPT_VALID_CATEGORY",
            "valid": True,
            "reason": "Budget category exists in the taxonomy.",
        }

    else:
        raise ValueError(f"Unknown anomaly scenario: {scenario_type}")
