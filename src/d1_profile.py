"""D1 data profile for the Olist dataset.

Usage:  python src/d1_profile.py data/raw

Prints, for every CSV: row/column counts, dtypes, nulls and unique values.
Then checks the date range, monthly order volume, timestamp anomalies,
review duplicates, the late-delivery rate and its link to review scores.
"""
import os
import sys

import pandas as pd

WINDOW = ("2017-01", "2018-08")  # full months used for analysis


def load(folder, name, **kw):
    return pd.read_csv(os.path.join(folder, name), **kw)


def profile_files(folder):
    print("=" * 70, "\nFILE PROFILE")
    total = 0
    for f in sorted(x for x in os.listdir(folder) if x.endswith(".csv")):
        df = load(folder, f)
        total += len(df)
        print(f"\n{f}: {len(df):,} rows x {df.shape[1]} cols")
        for c in df.columns:
            print(f"  {c:40s} {str(df[c].dtype):8s} nulls={df[c].isna().sum():>7,} unique={df[c].nunique():>8,}")
    print(f"\nTOTAL ROWS: {total:,}")


def check_orders(folder):
    print("\n" + "=" * 70, "\nORDERS")
    date_cols = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                 "order_delivered_customer_date", "order_estimated_delivery_date"]
    o = load(folder, "olist_orders_dataset.csv", parse_dates=date_cols)
    print(o.order_status.value_counts().to_string())
    print("\nPurchase range:", o.order_purchase_timestamp.min(), "->", o.order_purchase_timestamp.max())

    o["month"] = o.order_purchase_timestamp.dt.to_period("M").astype(str)
    print("\nOrders per month:\n", o.groupby("month").size().to_string())

    in_window = o.month.between(*WINDOW)
    print(f"\nWindow {WINDOW[0]}..{WINDOW[1]}: {in_window.sum():,} orders "
          f"({in_window.mean():.1%}); trimmed {(~in_window).sum():,}")

    bad = ((o.order_delivered_carrier_date < o.order_purchase_timestamp)
           | (o.order_delivered_customer_date < o.order_delivered_carrier_date))
    print("\nTimestamp anomalies")
    print("  carrier before purchase or delivery before carrier:", int(bad.sum()))
    print("  carrier before approval:", int((o.order_delivered_carrier_date < o.order_approved_at).sum()))
    print("  delivered status but no delivery date:",
          int(((o.order_status == "delivered") & o.order_delivered_customer_date.isna()).sum()))
    return o[in_window]


def check_reviews(folder, orders):
    print("\n" + "=" * 70, "\nREVIEWS AND DELIVERY")
    rv = load(folder, "olist_order_reviews_dataset.csv", parse_dates=["review_creation_date"])
    print("Orders with >1 review:", int((rv.order_id.value_counts() > 1).sum()))
    print("review_id reused across orders:", int(rv.review_id.duplicated().sum()))
    print("Reviews with a comment:", int(rv.review_comment_message.notna().sum()))

    d = orders[(orders.order_status == "delivered") & orders.order_delivered_customer_date.notna()].copy()
    d["late"] = d.order_delivered_customer_date.dt.normalize() > d.order_estimated_delivery_date.dt.normalize()
    d["days"] = (d.order_delivered_customer_date.dt.normalize() - d.order_purchase_timestamp.dt.normalize()).dt.days
    d["promised"] = (d.order_estimated_delivery_date.dt.normalize() - d.order_purchase_timestamp.dt.normalize()).dt.days
    print(f"\nDelivered orders in window: {len(d):,}; late rate {d.late.mean():.2%}")
    print(f"Avg delivery days {d.days.mean():.1f} vs promised {d.promised.mean():.1f}")

    latest = rv.sort_values("review_creation_date").drop_duplicates("order_id", keep="last")
    j = d.merge(latest[["order_id", "review_score"]], on="order_id")
    g = j.groupby("late").review_score.agg(avg_score="mean", n="count", low_rate=lambda s: (s <= 2).mean())
    print("\nReview score by late flag:\n", g.round(3).to_string())
    print(f"Share of low reviews from late orders: {j[j.review_score <= 2].late.mean():.1%}")


def check_customers(folder):
    print("\n" + "=" * 70, "\nCUSTOMERS")
    o = load(folder, "olist_orders_dataset.csv")
    c = load(folder, "olist_customers_dataset.csv")
    per_customer = o.merge(c, on="customer_id").groupby("customer_unique_id").order_id.nunique()
    print(f"Customers {len(per_customer):,}; repeat {(per_customer > 1).mean():.2%}")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    profile_files(folder)
    window_orders = check_orders(folder)
    check_reviews(folder, window_orders)
    check_customers(folder)
