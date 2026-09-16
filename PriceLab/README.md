# PriceLab

**PriceLab is a pricing and revenue decision-support app.** It helps a retail analyst answer:

> If we change a product's price, promotion, marketing spend, or position against a competitor, what happens to demand, revenue, profit, and margin?

Instead of stopping at a sales dashboard, PriceLab estimates product-level price elasticity, simulates business scenarios, and recommends the list price expected to maximize gross profit.

## What the MVP includes

- Interactive pricing, discount, competitor, and marketing controls
- Demand, revenue, profit, and margin forecasts
- Profit-maximizing price search across an allowed ±20% range
- Interpretable price-elasticity estimates
- Historical revenue, profit, and demand visuals
- Holdout model evaluation with R² and mean absolute error
- Five portfolio-ready SQL analyses
- 8 products, 4 categories, and 4,000+ reproducible daily observations

## Business workflow

1. Select a product.
2. Adjust the proposed list price and promotion.
3. Add assumptions about competitor price and marketing spend.
4. Compare the scenario with the current baseline.
5. Review the profit curve and recommended price.
6. Use the recommendation as a test hypothesis—not an automatic production change.

## Model

Each product uses a log-linear demand model:

`log(demand) = price + competitor price + marketing + discount + seasonality + weekend + trend`

The coefficient on log price is the estimated price elasticity. A value of `-1.6`, for example, means the model expects a 1% price increase to correspond to about a 1.6% demand decrease, with the other modeled factors held constant.

The app uses a chronological 80/20 train-test split so evaluation better reflects a real forecasting workflow.

## Run it on your Mac

Open Terminal, move into this folder, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit should open PriceLab in your browser. If it does not, copy the local URL shown in Terminal (usually `http://localhost:8501`).

The sample dataset is already included. To recreate it:

```bash
python3 src/generate_data.py
```

Run the tests with:

```bash
pytest -q
```

## Repository structure

```text
PriceLab/
├── app.py                         # Streamlit executive dashboard
├── data/
│   ├── pricelab_transactions.csv # Generated after setup
│   └── README.md                  # Data dictionary
├── sql/
│   └── pricing_analysis.sql       # Business analytics queries
├── src/
│   ├── generate_data.py           # Reproducible retail data generator
│   ├── modeling.py                # Interpretable demand model
│   └── pricing_engine.py          # Scenario + optimization logic
├── tests/
│   └── test_engine.py
├── resume_bullets.md
└── requirements.txt
```

## Strong next upgrades

1. Load the data into PostgreSQL and connect the dashboard to SQL.
2. Add inventory and minimum-margin constraints to the optimizer.
3. Compare the log-linear model with gradient boosting on forecast accuracy.
4. Add uncertainty ranges around demand and profit forecasts.
5. Replace the synthetic data with a public retail dataset and document all cleaning decisions.
6. Deploy the app and record a 60-second walkthrough for LinkedIn and your portfolio.

## Responsible use

This portfolio MVP uses synthetic observational data. Its recommendation shows what the fitted model predicts, not guaranteed causal impact. Real pricing changes should be validated through controlled tests and reviewed for inventory, customer, competitive, and legal constraints.

