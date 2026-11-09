"""Build the SQLite database: raw -> staging -> mart, then run data quality tests.

Usage:  python src/build_db.py data/raw
Output: data/processed/olist.db, data/processed/mart/*.csv (for Power BI and Excel)
        docs/data_quality_report.md
"""
import glob
import math
import os
import sqlite3
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILES = {
    "raw_orders": "olist_orders_dataset.csv",
    "raw_order_items": "olist_order_items_dataset.csv",
    "raw_reviews": "olist_order_reviews_dataset.csv",
    "raw_payments": "olist_order_payments_dataset.csv",
    "raw_customers": "olist_customers_dataset.csv",
    "raw_sellers": "olist_sellers_dataset.csv",
    "raw_products": "olist_products_dataset.csv",
    "raw_geolocation": "olist_geolocation_dataset.csv",
    "raw_category_translation": "product_category_name_translation.csv",
}
MART_TABLES = ["fact_orders", "fact_order_items", "dim_customer", "dim_seller", "dim_product", "dim_date"]


def haversine_km(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        return None
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def run_sql_folder(con, folder):
    for path in sorted(glob.glob(os.path.join(ROOT, "sql", folder, "*.sql"))):
        print(f"  running {os.path.relpath(path, ROOT)}")
        with open(path, encoding="utf-8") as f:
            con.executescript(f.read())


def main(raw_dir):
    out = os.path.join(ROOT, "data", "processed")
    os.makedirs(os.path.join(out, "mart"), exist_ok=True)
    db = os.path.join(out, "olist.db")
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db)
    con.create_function("haversine_km", 4, haversine_km, deterministic=True)

    print("1/4 raw")
    for table, file in RAW_FILES.items():
        df = pd.read_csv(os.path.join(raw_dir, file))
        df.to_sql(table, con, index=False)
        print(f"  {table}: {len(df):,} rows")

    print("2/4 staging")
    run_sql_folder(con, "02_staging")
    print("3/4 mart")
    run_sql_folder(con, "03_mart")
    con.commit()

    print("4/4 tests")
    with open(os.path.join(ROOT, "sql", "tests", "01_data_quality.sql"), encoding="utf-8") as f:
        tests = pd.read_sql(f.read(), con)
    tests["result"] = (tests.failing == tests.expected).map({True: "PASS", False: "FAIL"})
    print(tests.to_string(index=False))

    lines = ["# Data Quality Report", "",
             f"{(tests.result == 'PASS').sum()} of {len(tests)} tests pass. "
             "Tests marked *known* check that documented issues are flagged, not hidden.", "",
             "| Test | Failing rows | Expected | Result |", "|---|---|---|---|"]
    lines += [f"| {r.test} | {r.failing:,} | {r.expected:,} | {r.result} |" for r in tests.itertuples()]
    with open(os.path.join(ROOT, "docs", "data_quality_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    for t in MART_TABLES:
        df = pd.read_sql(f"SELECT * FROM {t}", con)
        df.to_csv(os.path.join(out, "mart", f"{t}.csv"), index=False)
        print(f"  exported {t}: {len(df):,} rows")
    con.close()
    if (tests.result == "FAIL").any():
        sys.exit("Data quality tests failed")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "raw"))
