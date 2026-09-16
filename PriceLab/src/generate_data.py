"""Generate a reproducible retail dataset for the PriceLab demo."""

from pathlib import Path

import numpy as np
import pandas as pd


PRODUCTS = [
    {"id": "P100", "name": "Everyday Sneakers", "category": "Footwear", "base_price": 68.0, "cost": 28.0, "base_demand": 72, "elasticity": -1.65},
    {"id": "P101", "name": "Trail Running Shoes", "category": "Footwear", "base_price": 112.0, "cost": 49.0, "base_demand": 48, "elasticity": -1.25},
    {"id": "P200", "name": "Classic Hoodie", "category": "Apparel", "base_price": 58.0, "cost": 20.0, "base_demand": 86, "elasticity": -1.85},
    {"id": "P201", "name": "Performance Leggings", "category": "Apparel", "base_price": 74.0, "cost": 24.0, "base_demand": 65, "elasticity": -1.45},
    {"id": "P300", "name": "Insulated Bottle", "category": "Accessories", "base_price": 34.0, "cost": 10.0, "base_demand": 104, "elasticity": -2.05},
    {"id": "P301", "name": "Everyday Backpack", "category": "Accessories", "base_price": 82.0, "cost": 31.0, "base_demand": 55, "elasticity": -1.35},
    {"id": "P400", "name": "Wireless Earbuds", "category": "Electronics", "base_price": 96.0, "cost": 43.0, "base_demand": 61, "elasticity": -2.20},
    {"id": "P401", "name": "Fitness Tracker", "category": "Electronics", "base_price": 129.0, "cost": 58.0, "base_demand": 43, "elasticity": -1.75},
]


def generate_dataset(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2025-01-01", "2026-06-30", freq="D")
    rows = []

    for product in PRODUCTS:
        for day_index, date in enumerate(dates):
            seasonal = 1 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365)
            holiday = 1.30 if date.month in (11, 12) else 1.0
            weekend = 1.10 if date.dayofweek >= 5 else 1.0
            trend = 1 + 0.00020 * day_index

            list_price = product["base_price"] * (
                1 + 0.035 * np.sin(day_index / 37) + rng.normal(0, 0.018)
            )
            discount_pct = float(rng.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20]))
            selling_price = list_price * (1 - discount_pct)
            competitor_price = product["base_price"] * (
                1.01 + 0.045 * np.sin(day_index / 43 + 0.5) + rng.normal(0, 0.025)
            )
            marketing_spend = max(100.0, rng.normal(1300, 360))

            demand = product["base_demand"]
            demand *= (selling_price / product["base_price"]) ** product["elasticity"]
            demand *= (competitor_price / product["base_price"]) ** 0.70
            demand *= (1 + marketing_spend / 7000) ** 0.55
            demand *= 1 + 0.80 * discount_pct
            demand *= seasonal * holiday * weekend * trend
            demand *= rng.lognormal(mean=0, sigma=0.09)
            units = max(1, int(round(demand)))

            revenue = selling_price * units
            gross_profit = (selling_price - product["cost"]) * units
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "category": product["category"],
                    "list_price": round(list_price, 2),
                    "discount_pct": round(discount_pct, 2),
                    "selling_price": round(selling_price, 2),
                    "competitor_price": round(competitor_price, 2),
                    "marketing_spend": round(marketing_spend, 2),
                    "units_sold": units,
                    "unit_cost": product["cost"],
                    "revenue": round(revenue, 2),
                    "gross_profit": round(gross_profit, 2),
                }
            )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "data" / "pricelab_transactions.csv"
    generate_dataset().to_csv(output, index=False)
    print(f"Created {output} with {len(generate_dataset()):,} rows")

