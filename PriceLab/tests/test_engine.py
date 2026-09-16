from pathlib import Path

import pandas as pd

from src.database import load_transactions
from src.pricing_engine import PricingEngine


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pricelab_transactions.csv"


def test_scenario_metrics_are_consistent():
    data = pd.read_csv(DATA_PATH)
    engine = PricingEngine(data, "Everyday Sneakers")
    result = engine.scenario(
        engine.base_list_price,
        engine.base_competitor_price,
        engine.base_marketing_spend,
        0.0,
    )
    assert result.expected_units > 0
    assert result.expected_revenue > result.expected_profit > 0
    assert 0 < result.margin_pct < 100


def test_optimizer_returns_price_in_allowed_range():
    data = pd.read_csv(DATA_PATH)
    engine = PricingEngine(data, "Wireless Earbuds")
    best, curve = engine.optimize(
        engine.base_competitor_price, engine.base_marketing_spend, 0.05
    )
    assert len(curve) == 81
    assert engine.base_list_price * 0.80 <= best.list_price <= engine.base_list_price * 1.20
    assert best.expected_profit == curve["expected_profit"].max()


def test_csv_fallback_loads_packaged_data(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    data, source, warning = load_transactions(DATA_PATH)
    assert source == "CSV"
    assert warning is None
    assert len(data) == 4368
