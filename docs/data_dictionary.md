# Data Dictionary — Mart

Star schema in `data/processed/olist.db`, also exported as CSV to `data/processed/mart/` for Power BI and Excel. Rebuild with `python src/build_db.py data/raw`.

```
               dim_date
                  │ purchase_date
dim_customer ── fact_orders ──< fact_order_items >── dim_product
  customer_id      order_id         order_id            product_id
                                       │ seller_id
                                    dim_seller
```

## fact_orders — one row per order (99,441)

| Column | Type | Description |
|---|---|---|
| order_id | text | Primary key |
| customer_id | text | → dim_customer |
| purchase_date, purchase_month | date, text | Purchase day and `YYYY-MM` |
| order_status | text | delivered, shipped, canceled, … |
| purchase_ts, approved_ts, carrier_ts, delivered_ts | datetime | Lifecycle timestamps |
| estimated_date | date | Date promised to the customer |
| in_window | 0/1 | Purchased Jan 2017 – Aug 2018 |
| chronology_error, carrier_before_approval | 0/1 | Data quality flags (see cleaning log) |
| n_items, n_sellers | int | Items and distinct sellers in the order |
| revenue, freight, payment_value | real (BRL) | Item prices, freight, amount paid |
| distance_km, same_state | real, 0/1 | Farthest seller → customer distance; all sellers in customer's state |
| any_handover_late | 0/1 | At least one seller missed its handover deadline |
| is_delivered, is_late | 0/1 | Delivered with a date; delivered after the promised day |
| promised_days, delivery_days, eta_buffer_days | days | Promise, actual, and slack |
| approval_days, handling_days, transit_days | days | Lifecycle stage durations |
| review_score, has_comment, is_low_review | int, 0/1, 0/1 | Latest review; low = 1–2 stars |

## fact_order_items — one row per item (112,650)

| Column | Type | Description |
|---|---|---|
| order_id, order_item_id | text, int | Composite key |
| product_id, seller_id | text | → dim_product, dim_seller |
| price, freight_value | real (BRL) | Item price and freight |
| shipping_limit_ts | datetime | Seller's deadline to hand over to the carrier |
| carrier_ts | datetime | Actual handover (order level) |
| handover_late | 0/1 | Handover after deadline |
| distance_km, same_state | real, 0/1 | Seller → customer |

## Dimensions

| Table | Rows | Columns |
|---|---|---|
| dim_customer | 99,441 | customer_id, customer_unique_id (real person), city, state, lat, lng, geo_level |
| dim_seller | 3,095 | seller_id, city, state, lat, lng, geo_level |
| dim_product | 32,951 | product_id, category (English), weight_g, volume_cm3, photos_qty |
| dim_date | 800 | date, year, month, year_month, weekday (0 = Sunday) |
