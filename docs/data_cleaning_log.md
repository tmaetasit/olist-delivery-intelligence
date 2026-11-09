# Data Cleaning Log

Every change made between the raw CSV files and the mart. Nothing is deleted: problem rows are **flagged** so each KPI can decide whether to use them. Code: `sql/02_staging/01_staging.sql`, `sql/03_mart/01_mart.sql`. Checks: [data_quality_report.md](data_quality_report.md).

| # | Issue | Rows | Decision | Column / rule |
|---|---|---|---|---|
| 1 | Orders outside full months (Sep–Dec 2016, Sep–Oct 2018) | 349 orders | Kept, flagged; excluded from analysis | `in_window = 0` |
| 2 | Carrier date before purchase, or delivery before carrier | 189 orders | Kept, flagged; excluded from all timing KPIs | `chronology_error = 1` |
| 3 | Handed to carrier before payment approval | 1,359 orders | Kept; excluded from seller handling days only | `carrier_before_approval = 1` |
| 4 | Status `delivered` but no delivery date | 8 orders | Not counted as delivered | `is_delivered = 0` |
| 5 | Orders with no items (mostly cancelled or unavailable) | 775 orders | Kept with `n_items = 0`; outside delivered scope | — |
| 6 | Orders with more than one review | 547 orders | Latest review kept | `ROW_NUMBER()` by review date |
| 7 | Same `review_id` on different orders | 814 rows | Reviews keyed on order, not review_id | `stg_reviews` |
| 8 | Geolocation duplicate rows | 261,831 rows | Removed before averaging | `SELECT DISTINCT` |
| 9 | Geolocation points outside Brazil | small number | Excluded from averages | lat −34…6, lng −74…−34 |
| 10 | Customers / sellers whose zip has no usable coordinates | 279 customers, 7 sellers | City average, then state average | `geo_level` = city / state |
| 11 | Products with no category | 610 products | Category `unknown` | `dim_product.category` |
| 12 | Categories with no English name | 2 categories | Translated manually | `pc_gamer`, `portable_kitchen_food_preparers` |
| 13 | Timestamps stored as text | all date columns | Converted with `datetime()` / `date()`; day counts use dates only | — |

## Derived fields

| Field | Rule |
|---|---|
| `is_late` | Delivery date (day) after estimated date |
| `handover_late` | Carrier date after the item's `shipping_limit_date` |
| `distance_km` | Haversine distance seller → customer; order level uses the farthest seller |
| `approval_days`, `handling_days`, `transit_days` | Day gaps between purchase → approval → carrier → delivery |
| `eta_buffer_days` | Estimated date − delivery date (positive = early) |
