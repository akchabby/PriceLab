"""Interpretable demand model used by the PriceLab scenario engine."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score


FEATURES = [
    "log_price",
    "log_competitor_price",
    "marketing_k",
    "discount_pct",
    "month_sin",
    "month_cos",
    "weekend",
    "trend",
]


def _feature_frame(df: pd.DataFrame, start_date: pd.Timestamp) -> pd.DataFrame:
    dates = pd.to_datetime(df["date"])
    return pd.DataFrame(
        {
            "log_price": np.log(df["selling_price"].clip(lower=0.01)),
            "log_competitor_price": np.log(df["competitor_price"].clip(lower=0.01)),
            "marketing_k": df["marketing_spend"] / 1000,
            "discount_pct": df["discount_pct"],
            "month_sin": np.sin(2 * np.pi * dates.dt.month / 12),
            "month_cos": np.cos(2 * np.pi * dates.dt.month / 12),
            "weekend": (dates.dt.dayofweek >= 5).astype(int),
            "trend": (dates - start_date).dt.days / 365,
        }
    )


@dataclass
class ModelMetrics:
    r2: float
    mae: float
    elasticity: float


class ProductDemandModel:
    """Log-linear demand model whose price coefficient is elasticity."""

    def __init__(self, product_data: pd.DataFrame):
        if product_data.empty:
            raise ValueError("Product data cannot be empty")
        self.data = product_data.sort_values("date").reset_index(drop=True).copy()
        self.data["date"] = pd.to_datetime(self.data["date"])
        self.start_date = self.data["date"].min()
        self.model = LinearRegression()
        self.metrics = self._fit()

    def _fit(self) -> ModelMetrics:
        x = _feature_frame(self.data, self.start_date)[FEATURES]
        y = np.log1p(self.data["units_sold"])
        split = max(int(len(self.data) * 0.80), 1)
        self.model.fit(x.iloc[:split], y.iloc[:split])
        test_x = x.iloc[split:]
        test_y = self.data["units_sold"].iloc[split:]
        if test_x.empty:
            predictions = np.expm1(self.model.predict(x))
            actual = self.data["units_sold"]
        else:
            predictions = np.expm1(self.model.predict(test_x))
            actual = test_y
        predictions = np.maximum(predictions, 0)
        return ModelMetrics(
            r2=float(r2_score(actual, predictions)),
            mae=float(mean_absolute_error(actual, predictions)),
            elasticity=float(self.model.coef_[FEATURES.index("log_price")]),
        )

    def predict(
        self,
        selling_price: float,
        competitor_price: float,
        marketing_spend: float,
        discount_pct: float,
        date: pd.Timestamp,
    ) -> float:
        row = pd.DataFrame(
            [
                {
                    "date": pd.Timestamp(date),
                    "selling_price": selling_price,
                    "competitor_price": competitor_price,
                    "marketing_spend": marketing_spend,
                    "discount_pct": discount_pct,
                }
            ]
        )
        x = _feature_frame(row, self.start_date)[FEATURES]
        return float(max(0, np.expm1(self.model.predict(x)[0])))

