-- SmartSpend AI Database Schema

PRAGMA foreign_keys = ON;

-- 1. USER PROFILE TABLE

CREATE TABLE IF NOT EXISTS user_profile (
    user_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    created_at TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('ACTIVE', 'INACTIVE'))
);

-- 2. ACCOUNT TABLE

CREATE TABLE IF NOT EXISTS account (
    account_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    account_type TEXT NOT NULL
        CHECK (account_type IN ('SAVINGS', 'CURRENT', 'CREDIT')),
    bank_name TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    opening_balance REAL NOT NULL,
    opened_date TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('ACTIVE', 'CLOSED', 'FROZEN')),

    FOREIGN KEY (user_id)
        REFERENCES user_profile(user_id),

    UNIQUE (user_id, account_id)
);

-- 3. MERCHANT TABLE

CREATE TABLE IF NOT EXISTS merchant (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    merchant_type TEXT NOT NULL,
    primary_category_code TEXT,
    country TEXT NOT NULL DEFAULT 'India',
    city TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('ACTIVE', 'INACTIVE'))
);

-- 4. CATEGORY TABLE

CREATE TABLE IF NOT EXISTS category (
    category_code TEXT PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    parent_category_code TEXT,
    description TEXT,

    FOREIGN KEY (parent_category_code)
        REFERENCES category(category_code)
);

-- 5. CATEGORY RULE TABLE

CREATE TABLE IF NOT EXISTS category_rule (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    merchant_pattern TEXT,
    description_pattern TEXT,
    category_code TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 1,
    confidence_score REAL NOT NULL
        CHECK (confidence_score BETWEEN 0 AND 1),
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    FOREIGN KEY (category_code)
        REFERENCES category(category_code)
);

-- 6. TRANSACTION TABLE

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    merchant_id TEXT,
    category_code TEXT,
    transaction_date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL CHECK (amount >= 0),
    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN ('DEBIT', 'CREDIT')),
    payment_method TEXT,
    currency TEXT NOT NULL DEFAULT 'INR',
    status TEXT NOT NULL
        CHECK (status IN ('COMPLETED', 'PENDING', 'FAILED', 'REVERSED')),
    created_at TEXT NOT NULL,

    FOREIGN KEY (account_id)
        REFERENCES account(account_id),

    FOREIGN KEY (merchant_id)
        REFERENCES merchant(merchant_id),

    FOREIGN KEY (category_code)
        REFERENCES category(category_code)
);

-- 7. BUDGET TABLE

CREATE TABLE IF NOT EXISTS budget (
    budget_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    category_code TEXT NOT NULL,
    budget_amount NUMERIC NOT NULL
        CHECK (budget_amount > 0),
    budget_period TEXT NOT NULL
        CHECK (budget_period IN ('WEEKLY', 'MONTHLY')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY (user_id)
        REFERENCES user_profile(user_id),

    FOREIGN KEY (category_code)
        REFERENCES category(category_code),

    CHECK (end_date >= start_date)
);

-- 8. RECURRING SERIES TABLE

CREATE TABLE IF NOT EXISTS recurring_series (
    recurring_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    merchant_id TEXT,
    category_code TEXT,
    recurring_name TEXT NOT NULL,
    expected_amount NUMERIC NOT NULL
        CHECK (expected_amount > 0),
    frequency TEXT NOT NULL
        CHECK (frequency IN ('WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY')),
    start_date TEXT NOT NULL,
    next_expected_date TEXT,
    status TEXT NOT NULL
        CHECK (status IN ('ACTIVE', 'PAUSED', 'CANCELLED')),
    confidence_score REAL
        CHECK (confidence_score BETWEEN 0 AND 1),

    FOREIGN KEY (user_id)
        REFERENCES user_profile(user_id),

    FOREIGN KEY (merchant_id)
        REFERENCES merchant(merchant_id),

    FOREIGN KEY (category_code)
        REFERENCES category(category_code)
);

-- 9. INSIGHT TABLE

CREATE TABLE IF NOT EXISTS insight (
    insight_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    insight_type TEXT NOT NULL
        CHECK (insight_type IN (
            'BUDGET_WARNING',
            'RECURRING_PAYMENT',
            'SPENDING_TREND',
            'UNUSUAL_SPENDING'
        )),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL
        CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    related_category_code TEXT,
    generated_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW'
        CHECK (status IN ('NEW', 'READ', 'DISMISSED')),

    FOREIGN KEY (user_id)
        REFERENCES user_profile(user_id),

    FOREIGN KEY (related_category_code)
        REFERENCES category(category_code)
);

-- 10. MERCHANT ALIAS TABLE

CREATE TABLE IF NOT EXISTS merchant_alias (
    alias_id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    alias_name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,

    FOREIGN KEY (merchant_id)
        REFERENCES merchant(merchant_id)
);

-- 11. TRANSACTION RECURRING MATCH TABLE

CREATE TABLE IF NOT EXISTS transaction_recurring_match (
    match_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    recurring_id TEXT NOT NULL,
    match_confidence REAL NOT NULL
        CHECK (match_confidence BETWEEN 0 AND 1),
    match_status TEXT NOT NULL
        CHECK (match_status IN ('MATCHED', 'REVIEW', 'REJECTED')),
    matched_at TEXT NOT NULL,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (recurring_id)
        REFERENCES recurring_series(recurring_id),

    UNIQUE (transaction_id, recurring_id)
);

-- 12. TRANSACTION CATEGORY HISTORY TABLE

CREATE TABLE IF NOT EXISTS transaction_category_history (
    history_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    old_category_code TEXT,
    new_category_code TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    confidence_score REAL
        CHECK (confidence_score BETWEEN 0 AND 1),
    changed_at TEXT NOT NULL,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (old_category_code)
        REFERENCES category(category_code),

    FOREIGN KEY (new_category_code)
        REFERENCES category(category_code)
);

-- 13. TRANSACTION CATEGORY GROUND TRUTH TABLE

CREATE TABLE IF NOT EXISTS transaction_category_ground_truth (
    ground_truth_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL UNIQUE,
    actual_category_code TEXT NOT NULL,
    verified_by TEXT NOT NULL,
    verified_at TEXT NOT NULL,

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id),

    FOREIGN KEY (actual_category_code)
        REFERENCES category(category_code)
);


-- 14. ENTITY EVENT TABLE

CREATE TABLE IF NOT EXISTS entity_event (
    event_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    event_description TEXT,
    created_at TEXT NOT NULL
);

-- 15. DATABASE INDEXES

CREATE INDEX IF NOT EXISTS idx_account_user
ON account(user_id);

CREATE INDEX IF NOT EXISTS idx_transaction_account_date
ON transactions(account_id, transaction_date);

CREATE INDEX IF NOT EXISTS idx_transaction_merchant
ON transactions(merchant_id);

CREATE INDEX IF NOT EXISTS idx_transaction_category
ON transactions(category_code);

CREATE INDEX IF NOT EXISTS idx_budget_user_category
ON budget(user_id, category_code);

CREATE INDEX IF NOT EXISTS idx_recurring_user
ON recurring_series(user_id);

CREATE INDEX IF NOT EXISTS idx_category_rule_priority
ON category_rule(priority);