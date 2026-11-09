-- MART: star schema for Power BI, Excel and the model.
-- Grain: fact_orders = one row per order; fact_order_items = one row per item.
-- Day counts use calendar dates (time of day ignored), as the KPI dictionary requires.

DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer AS
SELECT customer_id, customer_unique_id, city, state, lat, lng, geo_level FROM stg_customers;

DROP TABLE IF EXISTS dim_seller;
CREATE TABLE dim_seller AS
SELECT seller_id, city, state, lat, lng, geo_level FROM stg_sellers;

DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product AS
SELECT product_id, category, weight_g, volume_cm3, photos_qty FROM stg_products;

DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date AS
WITH RECURSIVE d(day) AS (
    SELECT date((SELECT MIN(purchase_ts) FROM stg_orders))
    UNION ALL
    SELECT date(day, '+1 day') FROM d
    WHERE day < date((SELECT MAX(COALESCE(delivered_ts, estimated_date)) FROM stg_orders))
)
SELECT day AS date,
       CAST(strftime('%Y', day) AS INTEGER) AS year,
       CAST(strftime('%m', day) AS INTEGER) AS month,
       strftime('%Y-%m', day)               AS year_month,
       CAST(strftime('%w', day) AS INTEGER) AS weekday   -- 0 = Sunday
FROM d;

DROP TABLE IF EXISTS fact_order_items;
CREATE TABLE fact_order_items AS
SELECT i.order_id, i.order_item_id, i.product_id, i.seller_id,
       i.price, i.freight_value, i.shipping_limit_ts,
       o.carrier_ts,
       CASE WHEN o.carrier_ts IS NULL THEN NULL
            WHEN o.carrier_ts > i.shipping_limit_ts THEN 1 ELSE 0 END AS handover_late,
       haversine_km(s.lat, s.lng, c.lat, c.lng) AS distance_km,
       CASE WHEN s.state = c.state THEN 1 ELSE 0 END AS same_state
FROM stg_order_items i
JOIN stg_orders o     ON o.order_id = i.order_id
LEFT JOIN stg_sellers s   ON s.seller_id = i.seller_id
LEFT JOIN stg_customers c ON c.customer_id = o.customer_id;

DROP TABLE IF EXISTS fact_orders;
CREATE TABLE fact_orders AS
WITH items AS (
    SELECT order_id,
           COUNT(*)                  AS n_items,
           COUNT(DISTINCT seller_id) AS n_sellers,
           SUM(price)                AS revenue,
           SUM(freight_value)        AS freight,
           MAX(distance_km)          AS distance_km,
           MIN(same_state)           AS same_state,
           MAX(handover_late)        AS any_handover_late
    FROM fact_order_items GROUP BY order_id
)
SELECT o.order_id, o.customer_id,
       date(o.purchase_ts) AS purchase_date, o.purchase_month, o.order_status,
       o.purchase_ts, o.approved_ts, o.carrier_ts, o.delivered_ts, o.estimated_date,
       o.in_window, o.chronology_error, o.carrier_before_approval,
       COALESCE(it.n_items, 0) AS n_items, it.n_sellers,
       it.revenue, it.freight, p.payment_value,
       it.distance_km, it.same_state, it.any_handover_late,
       CASE WHEN o.order_status = 'delivered' AND o.delivered_ts IS NOT NULL THEN 1 ELSE 0 END AS is_delivered,
       CASE WHEN o.delivered_ts IS NULL THEN NULL
            WHEN date(o.delivered_ts) > o.estimated_date THEN 1 ELSE 0 END AS is_late,
       julianday(o.estimated_date) - julianday(date(o.purchase_ts)) AS promised_days,
       CASE WHEN o.chronology_error = 0 THEN julianday(date(o.delivered_ts)) - julianday(date(o.purchase_ts)) END AS delivery_days,
       CASE WHEN o.chronology_error = 0 THEN julianday(o.estimated_date) - julianday(date(o.delivered_ts)) END AS eta_buffer_days,
       CASE WHEN o.chronology_error = 0 THEN julianday(date(o.approved_ts)) - julianday(date(o.purchase_ts)) END AS approval_days,
       CASE WHEN o.chronology_error = 0 AND o.carrier_before_approval = 0
            THEN julianday(date(o.carrier_ts)) - julianday(date(o.approved_ts)) END AS handling_days,
       CASE WHEN o.chronology_error = 0 THEN julianday(date(o.delivered_ts)) - julianday(date(o.carrier_ts)) END AS transit_days,
       r.review_score, r.has_comment,
       CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END AS is_low_review
FROM stg_orders o
LEFT JOIN items it       ON it.order_id = o.order_id
LEFT JOIN stg_payments p ON p.order_id = o.order_id
LEFT JOIN stg_reviews r  ON r.order_id = o.order_id;
