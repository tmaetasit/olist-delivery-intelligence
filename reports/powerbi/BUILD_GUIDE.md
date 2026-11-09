# Power BI Build Guide

About 2–3 hours. Every number on the finished report should match `src/ws1_diagnose.py`; that is your validation (US-01: within 0.1%).

## 1. Load data
1. Run `python src/build_db.py data/raw` → CSVs appear in `data/processed/mart/`.
2. Power BI Desktop → **Get data → Text/CSV** → load all six files: `fact_orders`, `fact_order_items`, `dim_customer`, `dim_seller`, `dim_product`, `dim_date`.
3. Power Query: set `purchase_date` and `dim_date[date]` to **Date**; timestamps to **Date/Time**; flags (`is_late`, `in_window`, …) to **Whole number**.

## 2. Model (Model view)
| From | To | Cardinality |
|---|---|---|
| fact_orders[customer_id] | dim_customer[customer_id] | Many → one |
| fact_orders[purchase_date] | dim_date[date] | Many → one |
| fact_order_items[order_id] | fact_orders[order_id] | Many → one (single direction) |
| fact_order_items[seller_id] | dim_seller[seller_id] | Many → one |
| fact_order_items[product_id] | dim_product[product_id] | Many → one |

Mark `dim_date` as the date table. Add a **report-level filter** `fact_orders[in_window] = 1`.

## 3. Measures
Create table `_Measures`, then paste each measure from `measures.dax`. Format rates as %, days with 1 decimal.

## 4. Pages
| Page | Visuals | Answers |
|---|---|---|
| Executive Overview | Cards: Total Orders, Revenue, AOV, Avg Review Score, On-time %. Line: Late Delivery Rate and Avg Review Score by `year_month` (two axes). Slicers: year, customer state | BQ1, US-01 |
| Delivery Performance | Filled map of `dim_customer[state]` coloured by Late Delivery Rate. Table: state, Total Orders, Late Delivery Rate, Avg Delivery Days, Avg Promised Days, ETA Buffer Days. Clustered bar: Avg Approval / Handling / Transit Days, split by Late Flag Label | BQ3, BQ5, US-03, US-05 |
| Customer Satisfaction | Column: Avg Review Score by days-late band (create a column `late_band` with SWITCH on `eta_buffer_days`). Scatter: categories, x = Late Delivery Rate, y = Low Review Rate, size = Total Orders | BQ2, BQ6, US-02, US-06 |
| Why Customers Complain | Added after WS2: bar of complaint categories, split late / on time | BQ7, US-09 |

## 5. Validate before you publish
| Check | Expected (from `ws1_diagnose.py`) |
|---|---|
| Late Delivery Rate, whole window | ≈ 6.8% |
| Avg Review Score, late vs on time | 2.27 vs 4.29 (all delivered) |
| Late rate, Mar 2018 | 19.0% |
| Late rate, state AL | 21.5% |

Save as `reports/powerbi/olist_delivery.pbix`, export each page as PNG into `reports/powerbi/` for the README.

## Page 3: Why Customers Complain

1. Run `python src/ws2_rules.py` to create `data/processed/mart/fact_complaints.csv` (one row per 1–2 star review with text).
2. Load it like the other CSVs (Csv.Document → PromoteHeaders → types, culture "en-US"). It needs no relationship: every visual on this page uses only this table.
3. Add the six measures at the end of `measures.dax`.
4. Visuals:
   - Card: `On-time Product Complaint %` (60.4%).
   - Clustered bar: Y = `complaint`, X = `On time` and `Late` (one series per status). Titled "On-time orders get low reviews for what arrives, not when".
   - Clustered column: X = `seller_count`, Y = `Missing Item Share` (47.6% multi-seller vs 12.8% single seller).
