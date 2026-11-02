import sqlite3
from config.settings import DATABASE_PATH


def evaluate_classifier():
    connection = sqlite3.connect(DATABASE_PATH)

    query = """
        SELECT
            t.category_code AS predicted,
            g.actual_category_code AS actual
        FROM transactions t
        JOIN transaction_category_ground_truth g
        ON t.transaction_id = g.transaction_id
    """

    results = connection.execute(query).fetchall()

    total = len(results)
    correct = sum(
        1 for predicted, actual in results
        if predicted == actual
    )

    accuracy = (correct / total) * 100 if total else 0

    print("CLASSIFICATION EVALUATION")
    print("=" * 35)
    print("Total transactions:", total)
    print("Correct predictions:", correct)
    print("Incorrect predictions:", total - correct)
    print(f"Accuracy: {accuracy:.2f}%")

    connection.close()


if __name__ == "__main__":
    evaluate_classifier()