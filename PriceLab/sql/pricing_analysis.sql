-- PriceLab portfolio queries (PostgreSQL syntax)

-- 1. Monthly revenue, profit, and gross margin by category
SELECT
    DATE_TRUNC('month', date) AS month,
    category,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(revenue), 0), 2) AS margin_pct
FROM transactions
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Product performance compared with the prior month
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', date) AS month,
        product_name,
        SUM(revenue) AS revenue
    FROM transactions
    GROUP BY 1, 2
)
SELECT
    month,
    product_name,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * (revenue / NULLIF(LAG(revenue) OVER (
        PARTITION BY product_name ORDER BY month
    ), 0) - 1), 2) AS revenue_growth_pct
FROM monthly
ORDER BY product_name, month;

-- 3. Promotion performance
SELECT
    CASE
        WHEN discount_pct = 0 THEN 'No promotion'
        WHEN discount_pct <= 0.10 THEN '1-10% off'
        ELSE 'More than 10% off'
    END AS promotion_band,
    ROUND(AVG(units_sold), 1) AS avg_units,
    ROUND(AVG(revenue), 2) AS avg_daily_revenue,
    ROUND(AVG(gross_profit), 2) AS avg_daily_profit
FROM transactions
GROUP BY 1
ORDER BY 1;

-- 4. Products priced above their competitors
SELECT
    product_name,
    ROUND(AVG(selling_price - competitor_price), 2) AS avg_price_premium,
    ROUND(AVG(units_sold), 1) AS avg_units_sold
FROM transactions
WHERE selling_price > competitor_price
GROUP BY product_name
ORDER BY avg_price_premium DESC;

-- 5. Rank products by total profit within category
SELECT
    category,
    product_name,
    ROUND(SUM(gross_profit), 2) AS total_profit,
    DENSE_RANK() OVER (
        PARTITION BY category ORDER BY SUM(gross_profit) DESC
    ) AS profit_rank
FROM transactions
GROUP BY category, product_name
ORDER BY category, profit_rank;

