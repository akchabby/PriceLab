"""PriceLab Streamlit dashboard."""

from pathlib import Path

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.pricing_engine import PricingEngine


st.set_page_config(page_title="PriceLab", page_icon="◈", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1320px;}
    [data-testid="stMetric"] {background: #f7f8fa; border: 1px solid #e8eaed;
      padding: 16px; border-radius: 12px;}
    .eyebrow {color:#5d6b7a; font-size:.78rem; font-weight:700; letter-spacing:.12em;}
    .recommendation {background:#eef8f3; border-left:5px solid #16805c;
      padding:16px 18px; border-radius:8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = Path(__file__).parent / "data" / "pricelab_transactions.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return frame


data = load_data()
products = sorted(data["product_name"].unique())

st.markdown('<div class="eyebrow">PRICING & REVENUE INTELLIGENCE</div>', unsafe_allow_html=True)
st.title("PriceLab")
st.caption("Test pricing decisions before making them. Forecast demand, revenue, profit, and margin from one scenario.")

with st.sidebar:
    st.header("Scenario controls")
    product = st.selectbox("Product", products)
    engine = PricingEngine(data, product)
    st.divider()
    price_change = st.slider("List price change", -20, 20, 0, format="%d%%")
    discount_pct = st.slider("Promotional discount", 0, 25, int(engine.base_discount_pct * 100), format="%d%%") / 100
    competitor_change = st.slider("Competitor price change", -15, 15, 0, format="%d%%")
    marketing_change = st.slider("Marketing spend change", -30, 50, 0, format="%d%%")
    st.caption("Assumptions are applied to the latest 30-day product baseline.")

scenario_list_price = engine.base_list_price * (1 + price_change / 100)
scenario_competitor = engine.base_competitor_price * (1 + competitor_change / 100)
scenario_marketing = engine.base_marketing_spend * (1 + marketing_change / 100)

baseline = engine.scenario(
    engine.base_list_price,
    engine.base_competitor_price,
    engine.base_marketing_spend,
    engine.base_discount_pct,
)
scenario = engine.scenario(
    scenario_list_price,
    scenario_competitor,
    scenario_marketing,
    discount_pct,
)
optimal, profit_curve = engine.optimize(
    scenario_competitor,
    scenario_marketing,
    discount_pct,
)

profit_delta = scenario.expected_profit - baseline.expected_profit
revenue_delta = scenario.expected_revenue - baseline.expected_revenue
unit_delta = scenario.expected_units - baseline.expected_units

overview_tab, trends_tab, model_tab = st.tabs(["Scenario", "Business trends", "Model details"])

with overview_tab:
    cols = st.columns(5)
    cols[0].metric("Selling price", f"${scenario.selling_price:,.2f}", f"{price_change:+d}% list price")
    cols[1].metric("Expected demand", f"{scenario.expected_units:,.0f}", f"{unit_delta:+,.1f} units")
    cols[2].metric("Expected revenue", f"${scenario.expected_revenue:,.0f}", f"${revenue_delta:+,.0f}")
    cols[3].metric("Expected profit", f"${scenario.expected_profit:,.0f}", f"${profit_delta:+,.0f}")
    cols[4].metric("Gross margin", f"{scenario.margin_pct:.1f}%")

    gap_pct = 100 * (optimal.list_price - scenario.list_price) / scenario.list_price
    if abs(gap_pct) <= 2:
        action = "Keep the proposed price"
        detail = "It is within 2% of the model's profit-maximizing price."
    elif gap_pct > 0:
        action = f"Test a higher list price near ${optimal.list_price:,.2f}"
        detail = f"The model estimates approximately ${optimal.expected_profit - scenario.expected_profit:,.0f} more profit per day at the optimum."
    else:
        action = f"Test a lower list price near ${optimal.list_price:,.2f}"
        detail = f"The added demand is estimated to produce approximately ${optimal.expected_profit - scenario.expected_profit:,.0f} more profit per day."
    st.markdown(
        f'<div class="recommendation"><b>Recommendation: {action}</b><br>{detail}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 1])
    with left:
        curve_chart = go.Figure()
        curve_chart.add_trace(
            go.Scatter(
                x=profit_curve["list_price"],
                y=profit_curve["expected_profit"],
                mode="lines",
                name="Expected profit",
                line=dict(color="#2457d6", width=3),
            )
        )
        curve_chart.add_vline(x=scenario.list_price, line_dash="dash", line_color="#d97904", annotation_text="Scenario")
        curve_chart.add_vline(x=optimal.list_price, line_dash="dot", line_color="#16805c", annotation_text="Optimal")
        curve_chart.update_layout(
            title="Profit response curve",
            xaxis_title="List price",
            yaxis_title="Expected daily profit",
            hovermode="x unified",
            margin=dict(l=15, r=15, t=55, b=15),
        )
        st.plotly_chart(curve_chart, use_container_width=True)
    with right:
        st.subheader("Decision summary")
        summary = pd.DataFrame(
            {
                "Metric": ["Current baseline", "Your scenario", "Model optimum", "Unit cost", "Price elasticity"],
                "Value": [
                    f"${baseline.selling_price:,.2f}",
                    f"${scenario.selling_price:,.2f}",
                    f"${optimal.selling_price:,.2f}",
                    f"${engine.unit_cost:,.2f}",
                    f"{engine.model.metrics.elasticity:.2f}",
                ],
            }
        )
        st.dataframe(summary, hide_index=True, use_container_width=True)
        elasticity = engine.model.metrics.elasticity
        if elasticity <= -1.5:
            st.info("Demand is highly price-sensitive. Small increases may reduce units noticeably, so test changes in stages.")
        else:
            st.info("Demand is moderately price-sensitive. The product may have room for a controlled price increase.")

with trends_tab:
    product_data = engine.product_data.copy()
    monthly = (
        product_data.set_index("date")
        .resample("MS")
        .agg(revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"), units=("units_sold", "sum"))
        .reset_index()
    )
    trend_chart = px.line(
        monthly,
        x="date",
        y=["revenue", "gross_profit"],
        title=f"Monthly performance — {product}",
        labels={"value": "Dollars", "variable": "Metric", "date": "Month"},
        color_discrete_sequence=["#2457d6", "#16805c"],
    )
    st.plotly_chart(trend_chart, use_container_width=True)
    left, right = st.columns(2)
    with left:
        scatter = px.scatter(
            product_data,
            x="selling_price",
            y="units_sold",
            color="discount_pct",
            title="Observed price vs. demand",
            labels={"selling_price": "Selling price", "units_sold": "Units sold", "discount_pct": "Discount"},
            color_continuous_scale="Blues",
        )
        slope, intercept = np.polyfit(product_data["selling_price"], product_data["units_sold"], 1)
        trend_x = np.linspace(product_data["selling_price"].min(), product_data["selling_price"].max(), 100)
        scatter.add_trace(
            go.Scatter(
                x=trend_x,
                y=slope * trend_x + intercept,
                mode="lines",
                name="Linear trend",
                line=dict(color="#d97904", width=3),
            )
        )
        st.plotly_chart(scatter, use_container_width=True)
    with right:
        category = (
            data.groupby("category", as_index=False)
            .agg(revenue=("revenue", "sum"), gross_profit=("gross_profit", "sum"))
        )
        category_chart = px.bar(
            category,
            x="category",
            y="gross_profit",
            title="Gross profit by category",
            color="gross_profit",
            color_continuous_scale="Greens",
        )
        st.plotly_chart(category_chart, use_container_width=True)

with model_tab:
    st.subheader("How the forecast works")
    st.write(
        "PriceLab uses a log-linear demand model for each product. It estimates demand from selling price, "
        "competitor price, marketing spend, promotion depth, seasonality, weekends, and trend. Because price "
        "is modeled in log form, its coefficient can be read directly as price elasticity."
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Holdout R²", f"{engine.model.metrics.r2:.2f}")
    m2.metric("Holdout MAE", f"{engine.model.metrics.mae:.1f} units")
    m3.metric("Estimated elasticity", f"{engine.model.metrics.elasticity:.2f}")
    st.warning(
        "This is a portfolio decision-support model trained on synthetic data. A production pricing decision "
        "would also require causal tests, inventory constraints, guardrails, and stakeholder review."
    )
