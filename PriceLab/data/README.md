# Data dictionary

`pricelab_transactions.csv` contains reproducible synthetic daily retail data from January 2025 through June 2026.

| Field | Meaning |
|---|---|
| date | Transaction summary date |
| product_id / product_name | Product identifier and display name |
| category | Product category |
| list_price | Price before promotion |
| discount_pct | Promotional discount as a decimal |
| selling_price | Actual price after discount |
| competitor_price | Comparable competitor price |
| marketing_spend | Daily product-level marketing spend |
| units_sold | Daily units sold |
| unit_cost | Cost per unit |
| revenue | Selling price × units sold |
| gross_profit | (Selling price − unit cost) × units sold |

The data is synthetic, so it is safe to publish. The generator is in `src/generate_data.py` and uses a fixed random seed for reproducibility.

