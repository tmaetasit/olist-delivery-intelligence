# Model Card — Late-Delivery Risk Score (WS3)

Reproduce: `python src/ws3_model.py` (about 1 minute).

## Decision (Gate: Go / no-go, week 7)

**Conditional go, with logistic regression.** The model finds 1.7× more late orders than the seller-history rule in its top 10% (24.6% vs 14.2% of late orders), so US-08 passes. But only 1 in 9 flagged orders is actually late, so the score may drive **cheap, customer-friendly actions only** (proactive message, wider ETA for high-risk orders), not seller penalties.

## Purpose
Score each order at payment approval with its risk of arriving after the promised date, so Operations can act before the delay.

## Data
| Item | Value |
|---|---|
| Population | Delivered orders, Jan 2017 – Aug 2018, valid timestamps, at least one item |
| Train | Jan 2017 – Mar 2018: 64,034 orders, 8.0% late |
| Test | Apr – Aug 2018: 31,985 orders, 4.4% late |
| Split | By purchase month (no random split), so the test imitates using the model on future orders |

## Features (known at payment approval)
Promised days, distance seller → customer, same state, customer and seller state, main category, items, sellers, price, freight, freight ratio, weight, volume, purchase weekday / hour / month, approval delay, seller handover window, **seller history** and **market load**.

**Leakage control:** seller late rate and market late rate use only orders *delivered before* the order was placed (`merge_asof`, strict). Seller late rate is smoothed toward 6% for sellers with little history.

## Results on the test months

| Model | PR-AUC | ROC-AUC | Recall @ top 10% | Precision @ top 10% |
|---|---|---|---|---|
| Random (base rate) | 0.043 | 0.49 | 8.9% | 3.9% |
| Rule: seller prior late rate | 0.052 | 0.53 | 14.2% | 6.3% |
| **Logistic regression** | **0.096** | **0.72** | **24.6%** | **10.9%** |
| LightGBM | 0.090 | 0.69 | 23.5% | 10.4% |

LightGBM did not beat the simpler model; removing the market-load features changed little (recall 25.1%). **Logistic regression is chosen**: as good, faster, and easier to explain to Operations.

## What drives risk (mean |SHAP|, LightGBM)
1. Orders placed in the last 7 days (market load)
2. Promised days (a short promise is easier to miss)
3. Customer state (north-east is riskier)
4. Recent market late rate
5. Seller's prior late rate
6. Distance

## Limits
- **Most delay happens in carrier transit** (WS1), which is not observable at approval, so the ceiling on accuracy is low.
- **Unstable by month:** recall@10% ranged from 38.6% (Apr 2018) to 7.1% (Aug 2018). The model must be monitored monthly and retrained.
- **Regime shift:** train contains the Nov 2017 and Feb–Mar 2018 peaks (8.0% late); test is calmer (4.4%).
- No carrier ID, no weather, no holidays in the data.

## Use rules
| Allowed | Not allowed |
|---|---|
| Proactive "your order may take longer" message to top-10% risk | Penalising or ranking sellers on the score |
| Adding buffer days to the ETA shown for top-10% risk | Cancelling or delaying orders |
| Prioritising Logistics follow-up | Using the score without monthly monitoring |
