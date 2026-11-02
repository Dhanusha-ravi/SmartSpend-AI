# SmartSpend-AI

An AI-powered personal finance analytics project that analyzes synthetic transaction data to categorize spending, identify recurring payments, compare expenses against budgets, and generate actionable spending insights.

## Project Overview

SmartSpend-AI simulates a personal finance management system using synthetic financial data.

The project focuses on:

- Transaction categorization and classification evaluation
- Recurring payment detection
- Monthly budget analysis
- Spending insights and alerts
- Financial anomaly detection and handling
- Ledger reconciliation
- Data validation and automated testing
- CSV and JSON data exports

## Dataset

The project uses two SQLite databases for separate purposes.

### Original Database

| Metric | Count |
|---|---:|
| Synthetic users | 1,000 |
| Accounts | 1,000 |
| Transactions | 500,016 |
| Ground truth records | 500,016 |
| Monthly budget records | 9,000 |
| Recurring payment matches | 11 |

### Test Database

| Metric | Count |
|---|---:|
| Synthetic users | 1,000 |
| Accounts | 1,000 |
| Transactions | 512,004 |
| Ground truth records | 512,004 |
| Monthly budget records | 108,000 |

The test database contains additional controlled records for analytics, anomaly handling, and budget testing.

**Dataset period:** January 2025 – December 2025.

All financial data is synthetic and does not represent real customers or bank accounts.

## Key Features

### 1. Transaction Categorization

- Categorizes debit and credit transactions.
- Applies merchant-based category rules.
- Uses merchant category fallback when no rule matches.
- Evaluates predicted categories against synthetic ground truth.

### 2. Recurring Payment Detection

- Identifies potential monthly and yearly recurring payments.
- Compares transaction amounts and dates.
- Calculates match confidence scores.
- Assigns MATCHED, REVIEW, or REJECTED statuses.

### 3. Budget Analysis

- Compares monthly spending against category budgets.
- Calculates remaining budget and utilization percentage.
- Identifies over-budget and near-limit categories.
- Uses nine supported budget categories.

### 4. Spending Insights

- Identifies the highest-spending category.
- Calculates total monthly spending.
- Generates category-wise spending summaries.
- Provides budget alerts.

### 5. Anomaly Handling

Implements decision logic for five financial data edge cases:

- Prevents internal transfers from being counted as expenses.
- Treats refunds as spending adjustments.
- Flags missing recurring payments for review.
- Normalizes timezone-aware transaction dates to UTC.
- Rejects invalid budget categories.

### 6. Ledger Reconciliation

- Generates signed transaction amounts.
- Calculates account balances from opening balances and transactions.
- Reconciles calculated closing balances.
- Separately flags accounts with negative balances.

### 7. Data Validation

- Checks duplicate transaction IDs.
- Checks missing and duplicate ground truth records.
- Validates amounts, dates, descriptions, and categories.
- Checks transaction types and statuses.
- Checks foreign key integrity.

## Testing

Automated tests are implemented using Pytest.

**Latest verified result: 48 tests passed.**

Run the test suite:

```bash
python -m pytest -v
```

Run data validation:

```bash
python -m src.validators.data_validator
```

## Technology Stack

- Python 3.13
- SQLite
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Faker
- Pytest

## Project Structure

```text
SmartSpend-AI/
├── config/
├── data/
│   └── exports/
├── database/
│   ├── schema.sql
│   ├── anomaly_schema.sql
│   ├── seed_data.sql
│   └── create_database.py
├── docs/
│   └── data_dictionary.md
├── src/
│   ├── generators/
│   ├── business_logic/
│   ├── analytics/
│   └── validators/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Exports

Generated exports are available under `data/exports/`.

| File | Rows |
|---|---:|
| transactions.csv | 500,012 |
| ground_truth.csv | 500,012 |
| budgets.csv | 9,000 |
| recurring_matches.csv | 11 |
| project_summary.json | Summary metadata |

## Setup

Clone the repository:

```bash
git clone https://github.com/Dhanusha-ravi/SmartSpend-AI.git
cd SmartSpend-AI
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it in Git Bash on Windows:

```bash
source venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

Run the automated tests:

```bash
python -m pytest -v
```

Run the data validator:

```bash
python -m src.validators.data_validator
```

---

**Note:** This project is developed for learning and demonstration purposes using synthetic financial data.
