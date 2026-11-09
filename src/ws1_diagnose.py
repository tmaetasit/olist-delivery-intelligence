"""WS1 Diagnose: where and why does delay happen?

Usage:  python src/ws1_diagnose.py
Needs:  data/processed/olist.db (run src/build_db.py first)
Output: printed tables + data/processed/ws1/*.csv
"""
import os
import sqlite3

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "processed", "ws1")


def section(title):
    print("\n" + "=" * 72 + f"\n{title}\n" + "=" * 72)


def main():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(os.path.join(ROOT, "data", "processed", "olist.db"))
    o = pd.read_sql("""
        SELECT f.*, c.state AS customer_state, c.customer_unique_id
        FROM fact_orders f JOIN dim_customer c USING (customer_id)
        WHERE in_window = 1 AND is_delivered = 1 AND chronology_error = 0""", con)
    items = pd.read_sql("""
        SELECT i.*, s.state AS seller_state, p.category
        FROM fact_order_items i
        JOIN fact_orders f USING (order_id)
        JOIN dim_seller s USING (seller_id)
        JOIN dim_product p USING (product_id)
        WHERE f.in_window = 1 AND f.is_delivered = 1 AND f.chronology_error = 0""", con)
    items = items.merge(o[["order_id", "is_late", "review_score", "is_low_review"]], on="order_id")
    print(f"Delivered orders analysed: {len(o):,}; items: {len(items):,}")

    section("1. Review score by days late (BQ2)")
    o["late_band"] = pd.cut(-o.eta_buffer_days, [-1e9, 0, 3, 7, 1e9],
                            labels=["on time", "1-3 days late", "4-7 days late", "8+ days late"])
    t = o.groupby("late_band", observed=True).agg(orders=("order_id", "size"),
                                                  avg_score=("review_score", "mean"),
                                                  low_review_rate=("is_low_review", "mean"))
    print(t.round(3).to_string()); t.to_csv(f"{OUT}/score_by_late_band.csv")

    section("2. Stage durations, days (BQ5)")
    stages = ["approval_days", "handling_days", "transit_days", "delivery_days", "promised_days", "eta_buffer_days"]
    t = o.groupby("is_late")[stages].mean().T.rename(columns={0: "on time", 1: "late"})
    t["late minus on time"] = t["late"] - t["on time"]
    print(t.round(2).to_string()); t.to_csv(f"{OUT}/stage_durations.csv")

    section("3. Late-order driver tree (BQ5)")
    late = o[o.is_late == 1]
    hl = late.any_handover_late.fillna(0)
    print(f"Late orders: {len(late):,}")
    print(f"  with a late seller handover:   {hl.mean():.1%}")
    print(f"  seller on time, still late:    {1 - hl.mean():.1%}  (carrier transit or ETA)")
    rate = o.groupby(o.any_handover_late.fillna(0))["is_late"].agg(["mean", "size"])
    print("\nLate rate by seller handover:\n", rate.rename(index={0: "handover on time", 1: "handover late"}).round(3).to_string())

    section("4. Customer states (BQ3), states with 100+ orders")
    t = o.groupby("customer_state").agg(orders=("order_id", "size"), late_rate=("is_late", "mean"),
                                         avg_delivery_days=("delivery_days", "mean"),
                                         avg_promised_days=("promised_days", "mean"),
                                         avg_eta_buffer=("eta_buffer_days", "mean"),
                                         avg_score=("review_score", "mean"))
    t = t[t.orders >= 100].sort_values("late_rate", ascending=False)
    print(t.round(3).head(10).to_string()); print("...lowest:\n", t.round(3).tail(3).to_string())
    t.to_csv(f"{OUT}/states.csv")
    print(f"\nCorrelation of state late rate with ETA buffer: {t.late_rate.corr(t.avg_eta_buffer):.2f}")

    section("5. Late rate by month (BQ1)")
    t = o.groupby("purchase_month").agg(orders=("order_id", "size"), late_rate=("is_late", "mean"),
                                        avg_score=("review_score", "mean"))
    print(t.round(3).to_string()); t.to_csv(f"{OUT}/monthly.csv")

    section("6. Seller concentration (BQ4)")
    s = items.groupby("seller_id").agg(items=("order_id", "size"), handover_late_rate=("handover_late", "mean"),
                                        late_items=("is_late", "sum"), avg_score=("review_score", "mean"))
    s = s.sort_values("late_items", ascending=False)
    s["cum_share_late"] = s.late_items.cumsum() / s.late_items.sum()
    top10 = int(len(s) * 0.10)
    print(f"Sellers: {len(s):,}. Top 10% ({top10}) by late items cause {s.cum_share_late.iloc[top10 - 1]:.1%} of late items")
    print(f"They handle {s['items'].iloc[:top10].sum() / s['items'].sum():.1%} of all items")
    big = s[s['items'] >= 30]
    print(f"Sellers with 30+ items: {len(big):,}; handover-late rate median {big.handover_late_rate.median():.1%}, "
          f"90th percentile {big.handover_late_rate.quantile(.9):.1%}")
    s.to_csv(f"{OUT}/sellers.csv")

    section("7. Categories (BQ6), 50+ orders")
    c = items.groupby("category").agg(orders=("order_id", "nunique"), late_rate=("is_late", "mean"),
                                       low_review_rate=("is_low_review", "mean"))
    c = c[c.orders >= 50]
    both = c[(c.late_rate > c.late_rate.median()) & (c.low_review_rate > c.low_review_rate.median())]
    print(f"Categories: {len(c)}; above median on both: {len(both)}")
    print(both.sort_values("low_review_rate", ascending=False).round(3).head(10).to_string())
    c.to_csv(f"{OUT}/categories.csv")

    section("8. Low reviews by delivery status (BQ7)")
    rv = o[o.review_score.notna()]
    low = rv[rv.is_low_review == 1]
    print(f"Low reviews: {len(low):,}; from late orders {low.is_late.mean():.1%}; from on-time {1 - low.is_late.mean():.1%}")
    print(f"Low reviews from on-time orders that have a comment: {low[low.is_late == 0].has_comment.mean():.1%}")
    multi = rv.groupby(rv.n_items > 1).is_low_review.mean()
    print(f"Low review rate, single-item vs multi-item orders: {multi.loc[False]:.1%} vs {multi.loc[True]:.1%}")
    ms = rv.groupby(rv.n_sellers > 1).is_low_review.mean()
    print(f"Low review rate, one seller vs several sellers: {ms.loc[False]:.1%} vs {ms.loc[True]:.1%}")

    section("9. Distance")
    o["dist_band"] = pd.cut(o.distance_km, [0, 100, 500, 1000, 2000, 1e9],
                            labels=["<100", "100-500", "500-1000", "1000-2000", "2000+"])
    t = o.groupby("dist_band", observed=True).agg(orders=("order_id", "size"), late_rate=("is_late", "mean"),
                                                  promised=("promised_days", "mean"), actual=("delivery_days", "mean"))
    print(t.round(3).to_string()); t.to_csv(f"{OUT}/distance.csv")


if __name__ == "__main__":
    main()
