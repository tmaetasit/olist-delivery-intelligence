# Data Quality Report

19 of 19 tests pass. Tests marked *known* check that documented issues are flagged, not hidden.

| Test | Failing rows | Expected | Result |
|---|---|---|---|
| fact_orders: order_id is unique | 0 | 0 | PASS |
| fact_orders: one row per raw order | 0 | 0 | PASS |
| fact_order_items: one row per raw item | 0 | 0 | PASS |
| fact_order_items: every item has a known seller | 0 | 0 | PASS |
| fact_order_items: every item has a known product | 0 | 0 | PASS |
| fact_orders: every order has a known customer | 0 | 0 | PASS |
| stg_reviews: at most one review per order | 0 | 0 | PASS |
| revenue reconciles to raw item prices (cents off) | 0 | 0 | PASS |
| review_score is between 1 and 5 | 0 | 0 | PASS |
| delivered orders have no negative delivery days | 0 | 0 | PASS |
| known: chronology errors flagged | 189 | 189 | PASS |
| known: carrier before approval flagged | 1,359 | 1,359 | PASS |
| known: delivered status without delivery date | 8 | 8 | PASS |
| known: orders without items | 775 | 775 | PASS |
| known: orders outside the analysis window | 349 | 349 | PASS |
| known: customers placed by city or state average (zip not usable) | 279 | 279 | PASS |
| known: sellers placed by city or state average (zip not usable) | 7 | 7 | PASS |
| customers with no coordinates at all | 0 | 0 | PASS |
| sellers with no coordinates at all | 0 | 0 | PASS |
