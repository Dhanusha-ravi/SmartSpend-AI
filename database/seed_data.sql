-- SMARTSPEND CATEGORY MASTER DATA

INSERT OR IGNORE INTO category
(category_code, category_name, parent_category_code, description)
VALUES
('FOOD', 'Food & Dining', NULL, 'Restaurants and food delivery'),
('GROCERY', 'Groceries', NULL, 'Daily household groceries'),
('TRANSPORT', 'Transportation', NULL, 'Travel and fuel expenses'),
('UTILITIES', 'Utilities', NULL, 'Electricity, water and internet'),
('HEALTH', 'Healthcare', NULL, 'Medical and pharmacy expenses'),
('SHOPPING', 'Shopping', NULL, 'Personal and household shopping'),
('ENTERTAINMENT', 'Entertainment', NULL, 'Movies and subscriptions'),
('EDUCATION', 'Education', NULL, 'Courses and learning expenses'),
('HOUSING', 'Housing', NULL, 'Rent and maintenance'),
('FINANCE', 'Finance', NULL, 'Banking and financial charges'),
('INCOME', 'Income', NULL, 'Salary and other income'),
('TRANSFER', 'Transfers', NULL, 'Money transfers between accounts'),
('OTHER', 'Other', NULL, 'Unclassified transactions');

-- MERCHANT MASTER DATA

INSERT OR IGNORE INTO merchant
(merchant_id, merchant_name, merchant_type, primary_category_code, country, city, status)
VALUES
('M001', 'Swiggy', 'FOOD_DELIVERY', 'FOOD', 'India', 'Bengaluru', 'ACTIVE'),
('M002', 'Zomato', 'FOOD_DELIVERY', 'FOOD', 'India', 'Bengaluru', 'ACTIVE'),
('M003', 'Amazon', 'E_COMMERCE', 'SHOPPING', 'India', 'Bengaluru', 'ACTIVE'),
('M004', 'Flipkart', 'E_COMMERCE', 'SHOPPING', 'India', 'Bengaluru', 'ACTIVE'),
('M005', 'BigBasket', 'GROCERY', 'GROCERY', 'India', 'Bengaluru', 'ACTIVE'),
('M006', 'Zepto', 'GROCERY', 'GROCERY', 'India', 'Bengaluru', 'ACTIVE'),
('M007', 'Uber', 'TRANSPORT', 'TRANSPORT', 'India', 'Bengaluru', 'ACTIVE'),
('M008', 'Ola', 'TRANSPORT', 'TRANSPORT', 'India', 'Bengaluru', 'ACTIVE'),
('M009', 'Netflix', 'SUBSCRIPTION', 'ENTERTAINMENT', 'India', 'Bengaluru', 'ACTIVE'),
('M010', 'Spotify', 'SUBSCRIPTION', 'ENTERTAINMENT', 'India', 'Bengaluru', 'ACTIVE'),
('M011', 'Airtel', 'TELECOM', 'UTILITIES', 'India', 'Bengaluru', 'ACTIVE'),
('M012', 'Bescom', 'ELECTRICITY', 'UTILITIES', 'India', 'Bengaluru', 'ACTIVE'),
('M013', 'Apollo Pharmacy', 'PHARMACY', 'HEALTH', 'India', 'Bengaluru', 'ACTIVE'),
('M014', 'Apollo Hospital', 'HOSPITAL', 'HEALTH', 'India', 'Bengaluru', 'ACTIVE'),
('M015', 'BookMyShow', 'ENTERTAINMENT', 'ENTERTAINMENT', 'India', 'Bengaluru', 'ACTIVE'),
('M016', 'Udemy', 'EDUCATION', 'EDUCATION', 'India', 'Bengaluru', 'ACTIVE'),
('M017', 'NoBroker', 'HOUSING', 'HOUSING', 'India', 'Bengaluru', 'ACTIVE'),
('M018', 'LIC', 'INSURANCE', 'FINANCE', 'India', 'Bengaluru', 'ACTIVE'),
('M019', 'Shell', 'FUEL', 'TRANSPORT', 'India', 'Bengaluru', 'ACTIVE'),
('M020', 'DMart', 'RETAIL', 'GROCERY', 'India', 'Bengaluru', 'ACTIVE');

-- MERCHANT ALIAS DATA

INSERT OR IGNORE INTO merchant_alias
(alias_id, merchant_id, alias_name, created_at)
VALUES
('A001', 'M001', 'SWIGGY', '2026-11-02'),
('A002', 'M001', 'SWIGGY INSTAMART', '2026-11-02'),
('A003', 'M002', 'ZOMATO', '2026-11-02'),
('A004', 'M003', 'AMZN', '2026-11-02'),
('A005', 'M003', 'AMAZON PAY', '2026-11-02'),
('A006', 'M004', 'FLIPKART', '2026-11-02'),
('A007', 'M005', 'BIGBASKET', '2026-11-02'),
('A008', 'M006', 'ZEPTO', '2026-11-02'),
('A009', 'M007', 'UBER TRIP', '2026-11-02'),
('A010', 'M008', 'OLA CABS', '2026-11-02'),
('A011', 'M009', 'NETFLIX', '2026-11-02'),
('A012', 'M010', 'SPOTIFY', '2026-11-02'),
('A013', 'M011', 'AIRTEL', '2026-11-02'),
('A014', 'M012', 'BESCOM', '2026-11-02'),
('A015', 'M015', 'BOOKMYSHOW', '2026-11-02');

-- TRANSACTION CATEGORY RULES

INSERT OR IGNORE INTO category_rule
(rule_id, rule_name, merchant_pattern, description_pattern,
 category_code, priority, confidence_score, is_active)
VALUES
('R001', 'Swiggy Rule', 'SWIGGY', NULL, 'FOOD', 1, 0.98, 1),
('R002', 'Zomato Rule', 'ZOMATO', NULL, 'FOOD', 1, 0.98, 1),
('R003', 'Amazon Rule', 'AMAZON', NULL, 'SHOPPING', 2, 0.95, 1),
('R004', 'Flipkart Rule', 'FLIPKART', NULL, 'SHOPPING', 2, 0.95, 1),
('R005', 'BigBasket Rule', 'BIGBASKET', NULL, 'GROCERY', 1, 0.98, 1),
('R006', 'Zepto Rule', 'ZEPTO', NULL, 'GROCERY', 1, 0.98, 1),
('R007', 'Uber Rule', 'UBER', NULL, 'TRANSPORT', 1, 0.98, 1),
('R008', 'Netflix Rule', 'NETFLIX', NULL, 'ENTERTAINMENT', 1, 0.99, 1),
('R009', 'Spotify Rule', 'SPOTIFY', NULL, 'ENTERTAINMENT', 1, 0.99, 1),
('R010', 'Airtel Rule', 'AIRTEL', NULL, 'UTILITIES', 2, 0.95, 1),
('R011', 'Bescom Rule', 'BESCOM', NULL, 'UTILITIES', 1, 0.98, 1),
('R012', 'Apollo Pharmacy Rule', 'APOLLO', NULL, 'HEALTH', 2, 0.90, 1),
('R013', 'Udemy Rule', 'UDEMY', NULL, 'EDUCATION', 1, 0.98, 1),
('R014', 'LIC Rule', 'LIC', NULL, 'FINANCE', 2, 0.90, 1),
('R015', 'Shell Fuel Rule', 'SHELL', NULL, 'TRANSPORT', 2, 0.95, 1);