\# SmartSpend AI – Data Dictionary



\## 1. UserProfile



| Field Name | Data Type | Required | Description | Validation |

|---|---|---|---|---|

| user\_id | VARCHAR(15) | Yes | Unique customer ID | USR-000001 format |

| first\_name | VARCHAR(50) | Yes | Customer first name | Not null |

| last\_name | VARCHAR(50) | Yes | Customer last name | Not null |

| email | VARCHAR(100) | Yes | Customer email | Unique, valid email |

| phone | VARCHAR(15) | No | Synthetic phone number | Valid format |

| city | VARCHAR(50) | Yes | Customer city | Not null |

| state | VARCHAR(50) | Yes | Customer state | Not null |

| country | VARCHAR(50) | Yes | Customer country | Not null |

| created\_at | DATETIME | Yes | Profile creation date | Valid datetime |

| status | VARCHAR(20) | Yes | Profile status | ACTIVE, INACTIVE |



Primary Key: user\_id



Unique Constraints: email



Lifecycle States: ACTIVE, INACTIVE



\## 2. Account



| Field Name | Data Type | Required | Description | Validation |

|---|---|---|---|---|

| account\_id | VARCHAR(30) | Yes | Unique account ID | ACC-<user-id>-01 format |

| user\_id | VARCHAR(15) | Yes | Account owner ID | Must exist in UserProfile |

| account\_type | VARCHAR(20) | Yes | Type of bank account | SAVINGS, CURRENT, CREDIT |

| bank\_name | VARCHAR(50) | Yes | Synthetic bank name | Not null |

| currency | CHAR(3) | Yes | Account currency | ISO currency code |

| opening\_balance | DECIMAL(14,2) | Yes | Initial account balance | Valid monetary amount |

| opened\_date | DATE | Yes | Account opening date | Valid date |

| status | VARCHAR(20) | Yes | Account status | ACTIVE, CLOSED, FROZEN |



Primary Key: account\_id



Foreign Key: user\_id references UserProfile(user\_id)



Relationship: UserProfile (1) → Account (Many)



Lifecycle States: ACTIVE, FROZEN, CLOSED

## 3. Merchant

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| merchant_id | VARCHAR(15) | Yes | Unique merchant ID | MER-000001 format |
| merchant_name | VARCHAR(100) | Yes | Merchant name | Not null |
| merchant_type | VARCHAR(30) | Yes | Business type | Valid business category |
| primary_category_code | VARCHAR(20) | No | Default spending category | Must exist in Category |
| country | VARCHAR(50) | Yes | Merchant country | Not null |
| city | VARCHAR(50) | No | Merchant city | Valid city |
| status | VARCHAR(20) | Yes | Merchant status | ACTIVE, INACTIVE |

Primary Key: merchant_id

Foreign Key: primary_category_code references Category(category_code)

Relationship: Merchant (1) → Transaction (Many)

Additional Rule: One merchant can have multiple aliases. Merchant aliases will be maintained separately.

Lifecycle States: ACTIVE, INACTIVE

## 4. Transaction

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| transaction_id | VARCHAR(20) | Yes | Unique transaction ID | TXN-2026-00000001 format |
| account_id | VARCHAR(30) | Yes | Account reference | Must exist in Account |
| merchant_id | VARCHAR(15) | No | Merchant reference | Must exist in Merchant |
| category_code | VARCHAR(20) | No | Assigned category | Must exist in Category |
| transaction_date | DATETIME | Yes | Transaction timestamp | Valid datetime |
| amount | DECIMAL(14,2) | Yes | Signed transaction amount | Non-zero |
| currency | CHAR(3) | Yes | Transaction currency | ISO currency code |
| description | VARCHAR(255) | Yes | Merchant transaction descriptor | Not null |
| transaction_type | VARCHAR(20) | Yes | Transaction type | DEBIT, CREDIT, REFUND, TRANSFER |
| status | VARCHAR(20) | Yes | Transaction status | PENDING, POSTED, REVERSED |
| ground_truth_category | VARCHAR(20) | Yes | Expected category label | Valid category code |
| created_at | DATETIME | Yes | Record creation timestamp | Valid datetime |

Primary Key: transaction_id

Foreign Keys:
- account_id references Account(account_id)
- merchant_id references Merchant(merchant_id)
- category_code references Category(category_code)

Relationship:
- Account (1) → Transaction (Many)
- Merchant (1) → Transaction (Many)
- Category (1) → Transaction (Many)

Business Rule:
- Expenses are negative.
- Income is positive.
- Refunds are positive.
- Transfers must not be counted as household spending twice.
- Ground-truth labels must be stored separately from model input features.

Lifecycle States: PENDING, POSTED, REVERSED

## 5. Category

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| category_code | VARCHAR(20) | Yes | Unique category code | Unique, uppercase |
| category_name | VARCHAR(50) | Yes | Category name | Not null |
| parent_category_code | VARCHAR(20) | No | Parent category | Must exist in Category |
| category_type | VARCHAR(20) | Yes | Income or expense | INCOME, EXPENSE, TRANSFER |
| description | VARCHAR(255) | No | Category explanation | Optional |
| status | VARCHAR(20) | Yes | Category status | ACTIVE, INACTIVE |
| effective_from | DATE | Yes | Start date of category | Valid date |
| effective_to | DATE | No | End date of category | Must be after effective_from |

Primary Key: category_code

Foreign Key: parent_category_code references Category(category_code)

Relationship:
- Category (1) → Transaction (Many)
- Category (1) → CategoryRule (Many)
- Category (1) → Budget (Many)

Example Categories:
- FOOD – Food and Dining
- RENT – House Rent
- SALARY – Salary Income
- TRANSPORT – Transportation
- SHOPPING – Shopping
- UTILITIES – Electricity and Water
- SUBSCRIPTION – Monthly Subscriptions
- TRANSFER – Money Transfers

Lifecycle States: ACTIVE, INACTIVE

## 6. CategoryRule

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| rule_id | VARCHAR(15) | Yes | Unique rule ID | RULE-000001 format |
| category_code | VARCHAR(20) | Yes | Target category | Must exist in Category |
| rule_name | VARCHAR(100) | Yes | Rule description | Not null |
| merchant_keyword | VARCHAR(100) | No | Merchant matching keyword | Case-insensitive |
| description_keyword | VARCHAR(100) | No | Transaction description keyword | Case-insensitive |
| priority | INTEGER | Yes | Rule execution priority | Positive integer |
| confidence_threshold | DECIMAL(4,3) | Yes | Minimum confidence | Between 0 and 1 |
| effective_from | DATE | Yes | Rule start date | Valid date |
| effective_to | DATE | No | Rule end date | After effective_from |
| status | VARCHAR(20) | Yes | Rule status | ACTIVE, INACTIVE |

Primary Key: rule_id

Foreign Key: category_code references Category(category_code)

Relationship:
- Category (1) → CategoryRule (Many)

Business Rules:
- Higher-priority rules execute first.
- Rules must be valid on the transaction date.
- Ambiguous matches must be flagged for review.
- Rule changes must preserve historical versions.

Lifecycle States: ACTIVE, INACTIVE

## 7. Budget

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| budget_id | VARCHAR(60) | Yes | Unique monthly budget ID | BUD-<user-id>-2026-01-<category-code> |
| user_id | VARCHAR(15) | Yes | Budget owner | Must exist in UserProfile |
| category_code | VARCHAR(20) | Yes | Budget category | Must exist in Category |
| budget_month | DATE | Yes | Budget month | First day of month |
| budget_amount | DECIMAL(14,2) | Yes | Monthly spending limit | Greater than zero |
| actual_spend | DECIMAL(14,2) | Yes | Actual eligible spending | Derived from transactions |
| remaining_amount | DECIMAL(14,2) | Yes | Remaining budget | Derived value |
| utilization_pct | DECIMAL(6,2) | Yes | Budget utilization percentage | Derived value |
| status | VARCHAR(20) | Yes | Budget status | ACTIVE, EXCEEDED, CLOSED |
| created_at | DATETIME | Yes | Budget creation time | Valid datetime |

Primary Key: budget_id

Foreign Keys:
- user_id references UserProfile(user_id)
- category_code references Category(category_code)

Relationship:
- UserProfile (1) → Budget (Many)
- Category (1) → Budget (Many)

Business Rules:
- Actual spending is calculated from eligible posted transactions.
- Refunds reduce net spending.
- Transfers are excluded from household spending.
- Remaining amount = Budget amount - Actual spend.
- Utilization percentage = Actual spend / Budget amount × 100.

Lifecycle States: ACTIVE, EXCEEDED, CLOSED

## 8. RecurringSeries

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| recurring_id | VARCHAR(15) | Yes | Unique recurring series ID | REC-000001 format |
| user_id | VARCHAR(15) | Yes | Customer reference | Must exist in UserProfile |
| account_id | VARCHAR(30) | Yes | Account reference | Must exist in Account |
| merchant_id | VARCHAR(15) | No | Merchant reference | Must exist in Merchant |
| category_code | VARCHAR(20) | Yes | Transaction category | Must exist in Category |
| series_name | VARCHAR(100) | Yes | Recurring payment name | Not null |
| expected_amount | DECIMAL(14,2) | Yes | Expected payment amount | Greater than zero |
| frequency | VARCHAR(20) | Yes | Payment frequency | WEEKLY, MONTHLY, QUARTERLY, YEARLY |
| start_date | DATE | Yes | Series start date | Valid date |
| end_date | DATE | No | Series end date | After start_date |
| next_expected_date | DATE | No | Next expected payment date | Derived from frequency |
| status | VARCHAR(20) | Yes | Series status | ACTIVE, PAUSED, COMPLETED, SKIPPED, REVIEW |
| created_at | DATETIME | Yes | Series creation time | Valid datetime |

Primary Key: recurring_id

Foreign Keys:
- user_id references UserProfile(user_id)
- account_id references Account(account_id)
- merchant_id references Merchant(merchant_id)
- category_code references Category(category_code)

Relationships:
- UserProfile (1) → RecurringSeries (Many)
- Account (1) → RecurringSeries (Many)
- Merchant (1) → RecurringSeries (Many)

Business Rules:
- Recurring payments are identified using amount, merchant and time intervals.
- Missing expected payments must be flagged.
- Actual payment history must be preserved.
- Recurring detection results must be evaluated against ground truth.

Lifecycle States: ACTIVE, PAUSED, COMPLETED, SKIPPED, REVIEW

## 9. Insight

| Field Name | Data Type | Required | Description | Validation |
|---|---|---|---|---|
| insight_id | VARCHAR(20) | Yes | Unique insight ID | INS-00000001 format |
| user_id | VARCHAR(15) | Yes | Customer reference | Must exist in UserProfile |
| account_id | VARCHAR(30) | No | Related account | Must exist in Account |
| insight_type | VARCHAR(30) | Yes | Insight classification | SPENDING, BUDGET, RECURRING, ANOMALY |
| title | VARCHAR(150) | Yes | Insight heading | Not null |
| description | TEXT | Yes | Insight explanation | Not null |
| period_start | DATE | Yes | Analysis start date | Valid date |
| period_end | DATE | Yes | Analysis end date | After period_start |
| metric_value | DECIMAL(14,2) | No | Calculated metric | Derived from source data |
| severity | VARCHAR(20) | Yes | Insight severity | LOW, MEDIUM, HIGH |
| generated_at | DATETIME | Yes | Insight generation time | Valid datetime |
| status | VARCHAR(20) | Yes | Insight status | ACTIVE, REVIEWED, DISMISSED |

Primary Key: insight_id

Foreign Keys:
- user_id references UserProfile(user_id)
- account_id references Account(account_id)

Relationship:
- UserProfile (1) → Insight (Many)
- Account (1) → Insight (Many)

Business Rules:
- Insights must be generated from actual transaction aggregations.
- Budget warnings must use calculated utilization.
- Recurring payment insights must reference detected recurring series.
- Anomaly insights must preserve the related transaction and issue type.
- Historical insights must not be overwritten.

Lifecycle States: ACTIVE, REVIEWED, DISMISSED

# 10. Entity Relationships and Cardinality

| Parent Entity | Child Entity | Cardinality | Relationship |
|---|---|---|---|
| UserProfile | Account | 1:N | One user can have multiple accounts |
| UserProfile | Budget | 1:N | One user can have multiple budgets |
| UserProfile | RecurringSeries | 1:N | One user can have multiple recurring series |
| UserProfile | Insight | 1:N | One user can have multiple insights |
| Account | Transaction | 1:N | One account can have multiple transactions |
| Account | RecurringSeries | 1:N | One account can have multiple recurring series |
| Merchant | Transaction | 1:N | One merchant can have multiple transactions |
| Category | Transaction | 1:N | One category can classify multiple transactions |
| Category | CategoryRule | 1:N | One category can have multiple rules |
| Category | Budget | 1:N | One category can have multiple budgets |
| Category | RecurringSeries | 1:N | One category can have multiple recurring series |
| UserProfile | Insight | 1:N | One user can receive multiple insights |

## Optional Relationships

- Transaction to Merchant: Optional.
- Transaction to Category: Optional until categorization.
- RecurringSeries to Merchant: Optional.
- Insight to Account: Optional.

## Many-to-Many Relationships

The following bridge tables will support many-to-many mappings:

1. MerchantAlias – supports multiple aliases for merchants.
2. TransactionRecurringMatch – maps recurring series to candidate transactions.
3. TransactionCategoryHistory – preserves category assignment history.

## Referential Integrity

- Every foreign key must reference an existing parent record.
- Primary keys must be unique and immutable.
- Deleting parent records must not silently delete historical transactions.
- State changes must be stored as separate events.
- Effective dates must be validated.
- All joins must be checked for unmatched records.