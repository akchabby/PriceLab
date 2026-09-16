-- Core PostgreSQL schema for PriceLab

CREATE TABLE IF NOT EXISTS transactions (
    date DATE NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    list_price NUMERIC(10, 2) NOT NULL CHECK (list_price > 0),
    discount_pct NUMERIC(5, 4) NOT NULL CHECK (discount_pct BETWEEN 0 AND 1),
    selling_price NUMERIC(10, 2) NOT NULL CHECK (selling_price > 0),
    competitor_price NUMERIC(10, 2) NOT NULL CHECK (competitor_price > 0),
    marketing_spend NUMERIC(12, 2) NOT NULL CHECK (marketing_spend >= 0),
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
    revenue NUMERIC(14, 2) NOT NULL,
    gross_profit NUMERIC(14, 2) NOT NULL,
    PRIMARY KEY (date, product_id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_product_date
    ON transactions (product_name, date);

CREATE INDEX IF NOT EXISTS idx_transactions_category
    ON transactions (category);

CREATE OR REPLACE VIEW monthly_product_performance AS
SELECT
    DATE_TRUNC('month', date)::date AS month,
    product_id,
    product_name,
    category,
    SUM(units_sold) AS units_sold,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(revenue), 0), 2) AS margin_pct
FROM transactions
GROUP BY 1, 2, 3, 4;

