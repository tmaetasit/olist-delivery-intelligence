-- STAGING: typed, de-duplicated, translated copies of the raw tables.
-- Rules come from BRD v0.2 and the D1 data profile.

DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    datetime(order_purchase_timestamp)       AS purchase_ts,
    datetime(order_approved_at)              AS approved_ts,
    datetime(order_delivered_carrier_date)   AS carrier_ts,
    datetime(order_delivered_customer_date)  AS delivered_ts,
    date(order_estimated_delivery_date)      AS estimated_date,
    strftime('%Y-%m', order_purchase_timestamp) AS purchase_month,
    CASE WHEN strftime('%Y-%m', order_purchase_timestamp) BETWEEN '2017-01' AND '2018-08'
         THEN 1 ELSE 0 END                   AS in_window,
    -- 189 orders: carrier before purchase, or delivered before carrier
    CASE WHEN order_delivered_carrier_date < order_purchase_timestamp
           OR order_delivered_customer_date < order_delivered_carrier_date
         THEN 1 ELSE 0 END                   AS chronology_error,
    -- 1,359 orders: handed to carrier before payment approval (kept, flagged)
    CASE WHEN order_delivered_carrier_date < order_approved_at
         THEN 1 ELSE 0 END                   AS carrier_before_approval
FROM raw_orders;

DROP TABLE IF EXISTS stg_order_items;
CREATE TABLE stg_order_items AS
SELECT
    order_id,
    CAST(order_item_id AS INTEGER)  AS order_item_id,
    product_id,
    seller_id,
    datetime(shipping_limit_date)   AS shipping_limit_ts,
    CAST(price AS REAL)             AS price,
    CAST(freight_value AS REAL)     AS freight_value
FROM raw_order_items;

-- One review per order: the latest (547 orders have more than one).
DROP TABLE IF EXISTS stg_reviews;
CREATE TABLE stg_reviews AS
SELECT order_id, review_id, review_score, has_comment, review_comment_message, review_created_date
FROM (
    SELECT
        order_id,
        review_id,
        CAST(review_score AS INTEGER) AS review_score,
        CASE WHEN review_comment_message IS NOT NULL AND trim(review_comment_message) <> ''
             THEN 1 ELSE 0 END        AS has_comment,
        review_comment_message,
        date(review_creation_date)    AS review_created_date,
        ROW_NUMBER() OVER (PARTITION BY order_id
                           ORDER BY review_creation_date DESC, review_answer_timestamp DESC) AS rn
    FROM raw_reviews
)
WHERE rn = 1;

DROP TABLE IF EXISTS stg_payments;
CREATE TABLE stg_payments AS
SELECT order_id,
       SUM(CAST(payment_value AS REAL)) AS payment_value,
       COUNT(*)                         AS n_payments,
       MAX(CAST(payment_installments AS INTEGER)) AS max_installments
FROM raw_payments
GROUP BY order_id;

-- Average coordinates per zip prefix, with city- and state-level fallbacks.
DROP TABLE IF EXISTS stg_geo_zip;
CREATE TABLE stg_geo_zip AS
SELECT CAST(geolocation_zip_code_prefix AS INTEGER) AS zip_prefix,
       AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng
FROM (SELECT DISTINCT * FROM raw_geolocation)          -- 261,831 duplicate rows removed
WHERE geolocation_lat BETWEEN -34 AND 6 AND geolocation_lng BETWEEN -74 AND -34  -- inside Brazil
GROUP BY 1;

DROP TABLE IF EXISTS stg_geo_city;
CREATE TABLE stg_geo_city AS
SELECT lower(geolocation_city) AS city, geolocation_state AS state,
       AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng
FROM (SELECT DISTINCT * FROM raw_geolocation)
WHERE geolocation_lat BETWEEN -34 AND 6 AND geolocation_lng BETWEEN -74 AND -34
GROUP BY 1, 2;

DROP TABLE IF EXISTS stg_geo_state;
CREATE TABLE stg_geo_state AS
SELECT geolocation_state AS state, AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng
FROM (SELECT DISTINCT * FROM raw_geolocation)
WHERE geolocation_lat BETWEEN -34 AND 6 AND geolocation_lng BETWEEN -74 AND -34
GROUP BY 1;

DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers AS
SELECT c.customer_id, c.customer_unique_id,
       CAST(c.customer_zip_code_prefix AS INTEGER) AS zip_prefix,
       lower(c.customer_city) AS city, c.customer_state AS state,
       COALESCE(z.lat, g.lat, st.lat) AS lat, COALESCE(z.lng, g.lng, st.lng) AS lng,
       CASE WHEN z.lat IS NOT NULL THEN 'zip' WHEN g.lat IS NOT NULL THEN 'city' ELSE 'state' END AS geo_level
FROM raw_customers c
LEFT JOIN stg_geo_zip  z ON z.zip_prefix = CAST(c.customer_zip_code_prefix AS INTEGER)
LEFT JOIN stg_geo_city g ON g.city = lower(c.customer_city) AND g.state = c.customer_state
LEFT JOIN stg_geo_state st ON st.state = c.customer_state;

DROP TABLE IF EXISTS stg_sellers;
CREATE TABLE stg_sellers AS
SELECT s.seller_id,
       CAST(s.seller_zip_code_prefix AS INTEGER) AS zip_prefix,
       lower(s.seller_city) AS city, s.seller_state AS state,
       COALESCE(z.lat, g.lat, st.lat) AS lat, COALESCE(z.lng, g.lng, st.lng) AS lng,
       CASE WHEN z.lat IS NOT NULL THEN 'zip' WHEN g.lat IS NOT NULL THEN 'city' ELSE 'state' END AS geo_level
FROM raw_sellers s
LEFT JOIN stg_geo_zip  z ON z.zip_prefix = CAST(s.seller_zip_code_prefix AS INTEGER)
LEFT JOIN stg_geo_city g ON g.city = lower(s.seller_city) AND g.state = s.seller_state
LEFT JOIN stg_geo_state st ON st.state = s.seller_state;

-- English category names; 2 categories lack a translation, 610 products lack a category.
DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products AS
SELECT p.product_id,
       COALESCE(t.product_category_name_english,
                CASE p.product_category_name
                     WHEN 'pc_gamer' THEN 'pc_gamer'
                     WHEN 'portateis_cozinha_e_preparadores_de_alimentos' THEN 'portable_kitchen_food_preparers'
                END,
                'unknown') AS category,
       CAST(p.product_weight_g AS REAL) AS weight_g,
       CAST(p.product_length_cm AS REAL) * CAST(p.product_height_cm AS REAL) * CAST(p.product_width_cm AS REAL) AS volume_cm3,
       CAST(p.product_photos_qty AS INTEGER) AS photos_qty
FROM raw_products p
LEFT JOIN raw_category_translation t ON t.product_category_name = p.product_category_name;
