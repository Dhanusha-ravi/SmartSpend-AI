# SmartSpend-AI



An AI-powered personal finance analytics project that analyzes synthetic transaction data to categorize spending, identify recurring payments, compare household expenses against budgets, and generate spending insights.



## Project Overview



SmartSpend-AI simulates a personal finance management system using synthetic financial data.



The project focuses on:

- Transaction categorization

- Recurring payment detection

- Monthly budget analysis

- Spending insights and alerts

- Data validation and testing

- CSV and JSON data exports



## Dataset



| Metric | Count |
|---|---:|
| Synthetic users | 1,000 |
| Accounts | 1,000 |
| Transactions | 500,012 |
| Ground truth records | 500,012 |
| Monthly budget records | 9,000 |
| Recurring payment matches | 11 |



**Dataset period:** January 2025 – December 2025



The dataset contains 500,000 generated transactions and 12 additional controlled transactions used to test recurring payment detection.



All financial data is synthetic and does not represent real customers or bank accounts.



## Key Features



### 1. Transaction Categorization

- Categorizes debit and credit transactions.

- Uses merchant-based category rules.

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



### 4. Spending Insights

- Identifies the highest-spending category.

- Calculates total monthly spending.

- Generates category-wise spending summaries.

- Provides budget alerts.



### 5. Data Validation

- Checks duplicate transaction IDs.

- Checks missing ground truth records.

- Validates amounts, dates, descriptions, and categories.

- Checks foreign key integrity.



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

│   ├── raw/

│   ├── processed/

│   ├── ground_truth/

│   └── exports/

├── database/

│   ├── schema.sql

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



## Setup



## Setup

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