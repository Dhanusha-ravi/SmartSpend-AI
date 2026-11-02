CREATE TABLE IF NOT EXISTS anomaly_ground_truth (
    anomaly_id TEXT PRIMARY KEY,
    scenario_type TEXT NOT NULL,
    transaction_id TEXT,
    expected_decision TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
    created_at TEXT NOT NULL,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id)
);