-- DATA QUALITY TESTS
-- Each test returns one row: test name, rows that break the rule, rows expected.
-- A test passes when failing = expected. Non-zero expectations are known issues
-- documented in the D1 data profile and handled by flags, not deletions.

SELECT 'fact_orders: order_id is unique' AS test,
       COUNT(*) - COUNT(DISTINCT order_id) AS failing, 0 AS expected FROM fact_orders
UNION ALL
SELECT 'fact_orders: one row per raw order',
       ABS((SELECT COUNT(*) FROM raw_orders) - (SELECT COUNT(*) FROM fact_orders)), 0
UNION ALL
SELECT 'fact_order_items: one row per raw item',
       ABS((SELECT COUNT(*) FROM raw_order_items) - (SELECT COUNT(*) FROM fact_order_items)), 0
UNION ALL
SELECT 'fact_order_items: every item has a known seller',
       COUNT(*), 0 FROM fact_order_items WHERE seller_id NOT IN (SELECT seller_id FROM dim_seller)
UNION ALL
SELECT 'fact_order_items: every item has a known product',
       COUNT(*), 0 FROM fact_order_items WHERE product_id NOT IN (SELECT product_id FROM dim_product)
UNION ALL
SELECT 'fact_orders: every order has a known customer',
       COUNT(*), 0 FROM fact_orders WHERE customer_id NOT IN (SELECT customer_id FROM dim_customer)
UNION ALL
SELECT 'stg_reviews: at most one review per order',
       COUNT(*) - COUNT(DISTINCT order_id), 0 FROM stg_reviews
UNION ALL
SELECT 'revenue reconciles to raw item prices (cents off)',
       CAST(ROUND(ABS((SELECT SUM(revenue) FROM fact_orders) - (SELECT SUM(CAST(price AS REAL)) FROM raw_order_items)) * 100) AS INTEGER), 0
UNION ALL
SELECT 'review_score is between 1 and 5',
       COUNT(*), 0 FROM fact_orders WHERE review_score IS NOT NULL AND review_score NOT BETWEEN 1 AND 5
UNION ALL
SELECT 'delivered orders have no negative delivery days',
       COUNT(*), 0 FROM fact_orders WHERE delivery_days < 0
UNION ALL
SELECT 'known: chronology errors flagged',
       SUM(chronology_error), 189 FROM fact_orders
UNION ALL
SELECT 'known: carrier before approval flagged',
       SUM(carrier_before_approval), 1359 FROM fact_orders
UNION ALL
SELECT 'known: delivered status without delivery date',
       COUNT(*), 8 FROM fact_orders WHERE order_status = 'delivered' AND delivered_ts IS NULL
UNION ALL
SELECT 'known: orders without items',
       COUNT(*), 775 FROM fact_orders WHERE n_items = 0
UNION ALL
SELECT 'known: orders outside the analysis window',
       COUNT(*), 349 FROM fact_orders WHERE in_window = 0
UNION ALL
SELECT 'known: customers placed by city or state average (zip not usable)',
       SUM(geo_level <> 'zip'), 279 FROM dim_customer
UNION ALL
SELECT 'known: sellers placed by city or state average (zip not usable)',
       SUM(geo_level <> 'zip'), 7 FROM dim_seller
UNION ALL
SELECT 'customers with no coordinates at all',
       COUNT(*), 0 FROM dim_customer WHERE lat IS NULL
UNION ALL
SELECT 'sellers with no coordinates at all',
       COUNT(*), 0 FROM dim_seller WHERE lat IS NULL;
