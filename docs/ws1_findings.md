# WS1 Findings — Where and Why Delay Happens

Delivered orders, Jan 2017 – Aug 2018, excluding the 189 with out-of-order timestamps (96,019 orders). Reproduce: `python src/ws1_diagnose.py` and `python src/ws1_process_mining.py`.

## Headline

**Late orders are lost in carrier transit, not at the seller:** a late order spends 27.9 days between carrier pickup and delivery against 7.9 for an on-time order, while seller handling adds only 2.9 extra days. 72% of late orders had a seller who handed over on time.

## 1. Satisfaction drops with every day of delay (BQ2)

| Delivery | Orders | Avg score | Low-review rate |
|---|---|---|---|
| On time | 89,490 | 4.29 | 9% |
| 1–3 days late | 1,868 | 3.29 | 32% |
| 4–7 days late | 1,801 | 2.11 | 66% |
| 8+ days late | 2,860 | 1.70 | 77% |

Even one to three days late costs a full star. Warning customers early may protect part of that point.

## 2. The delay is in transit (BQ5)

| Stage (days) | On time | Late | Gap |
|---|---|---|---|
| Payment approval | 0.5 | 0.6 | +0.1 |
| Seller handling | 2.5 | 5.4 | +2.9 |
| **Carrier transit** | **7.9** | **27.9** | **+19.9** |
| Promised | 24.4 | 23.3 | −1.1 |

Process mining (pm4py): 98.6% of orders follow the expected path *placed → approved → handed to carrier → delivered*; 1.4% show out-of-order timestamps, mostly handover before approval (1.2%).

## 3. Driver tree of late orders

- Late orders: 6,529
  - Seller handed over late: **27.7%** → seller problem
  - Seller on time, order still late: **72.3%** → carrier or ETA problem
- A late handover raises the late rate from 5.4% to 21.1% (3.9×), so sellers still matter.

## 4. The promise is not calibrated by region (BQ3)

- Late rate ranges from **21.5% (Alagoas)** to **2.8% (Amazonas)** among states with 100+ orders.
- Across states, late rate correlates **−0.72** with the average ETA buffer: where the promise carries less slack, more orders miss it. The ETA appears to use a buffer that does not fit each route.
- North-east states (AL, MA, SE, PI, CE, BA) dominate the top of the list.
- Late rate rises with distance: 4.5% under 100 km, 12.1% over 2,000 km.

## 5. Delay spikes in peak months (BQ1)

Late rate is usually 3–7%, but reached **12.4% in Nov 2017** (the month with the most orders) and **14.1% / 19.0% in Feb / Mar 2018**. Average review score fell to 3.81 in Mar 2018. Capacity planning before peaks is a lever; the cause of the Feb–Mar spike needs checking with Operations.

## 6. Sellers (BQ4)

The 10% of sellers with the most late items cause 73.8% of late items but also handle 62.4% of all items, so the concentration mostly reflects volume. Among sellers with 30+ items, the median handover-late rate is 4.9% and the 90th percentile is 25.0%: a seller SLA should target that tail.

## 7. Categories (BQ6)

18 of 59 categories (50+ orders) are above the median on both late rate and low-review rate, led by office furniture (25% low reviews), audio, home comfort, bed/bath/table and furniture: bulky items.

## 8. Clues for WS2 (BQ7)

- 67% of low reviews come from **on-time** orders; 78% of those have a comment, so WS2 has text to work with.
- Orders with **several sellers** have a 47% low-review rate against 12% for one seller; multi-item orders 27% vs 11%. Hypothesis: items arrive separately and customers think part of the order is missing. WS2 should test this.
