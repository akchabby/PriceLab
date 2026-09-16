"""Scenario and optimization logic for PriceLab."""

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from src.modeling import ProductDemandModel


@dataclass
class ScenarioResult:
    list_price: float
    selling_price: float
    expected_units: float
    expected_revenue: float
    expected_profit: float
    margin_pct: float

    def to_dict(self) -> dict:
        return asdict(self)


class PricingEngine:
    def __init__(self, data: pd.DataFrame, product_name: str):
        self.product_data = data.loc[data["product_name"] == product_name].copy()
        if self.product_data.empty:
            raise ValueError(f"Unknown product: {product_name}")
        self.product_data["date"] = pd.to_datetime(self.product_data["date"])
        self.model = ProductDemandModel(self.product_data)
        recent = self.product_data.sort_values("date").tail(30)
        self.base_list_price = float(recent["list_price"].median())
        self.base_competitor_price = float(recent["competitor_price"].median())
        self.base_marketing_spend = float(recent["marketing_spend"].median())
        self.base_discount_pct = float(recent["discount_pct"].median())
        self.unit_cost = float(recent["unit_cost"].median())
        self.forecast_date = self.product_data["date"].max() + pd.Timedelta(days=1)

    def scenario(
        self,
        list_price: float,
        competitor_price: float,
        marketing_spend: float,
        discount_pct: float,
    ) -> ScenarioResult:
        selling_price = list_price * (1 - discount_pct)
        units = self.model.predict(
            selling_price=selling_price,
            competitor_price=competitor_price,
            marketing_spend=marketing_spend,
            discount_pct=discount_pct,
            date=self.forecast_date,
        )
        revenue = selling_price * units
        profit = (selling_price - self.unit_cost) * units
        margin = 100 * profit / revenue if revenue else 0
        return ScenarioResult(
            list_price=round(list_price, 2),
            selling_price=round(selling_price, 2),
            expected_units=round(units, 1),
            expected_revenue=round(revenue, 2),
            expected_profit=round(profit, 2),
            margin_pct=round(margin, 1),
        )

    def optimize(
        self,
        competitor_price: float,
        marketing_spend: float,
        discount_pct: float,
        min_change: float = -0.20,
        max_change: float = 0.20,
    ) -> tuple[ScenarioResult, pd.DataFrame]:
        candidate_prices = np.linspace(
            self.base_list_price * (1 + min_change),
            self.base_list_price * (1 + max_change),
            81,
        )
        results = [
            self.scenario(price, competitor_price, marketing_spend, discount_pct).to_dict()
            for price in candidate_prices
        ]
        curve = pd.DataFrame(results)
        best = curve.loc[curve["expected_profit"].idxmax()]
        return ScenarioResult(**best.to_dict()), curve
