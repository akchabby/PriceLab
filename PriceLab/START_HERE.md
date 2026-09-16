# Start here, Abby

## Your first goal

Get the dashboard running and be able to explain this sentence:

> PriceLab estimates how demand changes with price, then searches for the price expected to produce the highest gross profit.

## 1. Open the project on your Mac

Download and unzip `PriceLab.zip`. Open Terminal, type `cd ` with a space, drag the unzipped **PriceLab** folder into Terminal, and press Return.

## 2. Install and launch it

Copy these commands into Terminal one at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard should open in your browser. Keep Terminal open while you use it. Press **Control + C** in Terminal when you want to stop it.

At first, the sidebar will say **Data source: packaged CSV**. That is normal. Once the basic app works, follow `POSTGRES_SETUP.md` to turn on PostgreSQL. The sidebar will then show a green **Data source: PostgreSQL** message.

## 3. Try this first scenario

1. Select **Wireless Earbuds**.
2. Set **List price change** to `+5%`.
3. Set **Promotional discount** to `5%`.
4. Set **Competitor price change** to `+3%`.
5. Set **Marketing spend change** to `+10%`.
6. Compare expected demand, revenue, profit, and the model's recommended price.

Write down what changed and why. That becomes your first project explanation.

## What to understand before putting it on your resume

- **Revenue** = selling price × units sold
- **Gross profit** = (selling price − unit cost) × units sold
- **Price elasticity** measures how strongly demand responds to price
- A price can increase revenue but still reduce profit—or do the reverse
- The recommendation is a model estimate, not proof that the price change causes the result

## Your next three upgrades

1. Run the queries in `sql/pricing_analysis.sql` and save two useful findings.
2. Add an inventory limit so the optimizer cannot recommend more units than the company has available.
3. Replace the synthetic data with a public retail dataset and document your cleaning steps.

## Interview explanation

> I built PriceLab to connect predictive modeling with a real pricing decision. I created a PostgreSQL data layer and an interactive dashboard where a user can change price, promotions, competitor pricing, and marketing spend, then compare the expected effect on demand, revenue, gross profit, and margin. I used an interpretable log-linear model to estimate price elasticity and added an optimizer that tests a range of prices to find the highest predicted profit. I evaluated the model on later dates instead of random rows to better represent forecasting.
