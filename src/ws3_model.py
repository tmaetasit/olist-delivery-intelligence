"""WS3 Predict: can we see a late order coming at payment approval?

Usage:  python src/ws3_model.py
Needs:  data/processed/olist.db
Output: printed metrics, data/processed/ws3/{scores_test.csv, shap_importance.csv, metrics.csv}

Rules (BRD v0.2):
  - Features use only what is known at payment approval.
  - Seller history and market load come only from orders DELIVERED before this order was placed.
  - Train/test split by time, never at random.
"""
import os
import sqlite3

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "processed", "ws3")
TEST_FROM = "2018-04"          # train: Jan 2017 – Mar 2018, test: Apr – Aug 2018
SEED = 42


def load(con):
    o = pd.read_sql("""
        SELECT f.order_id, f.purchase_ts, f.approved_ts, f.delivered_ts, f.purchase_month, f.is_late,
               f.promised_days, f.n_items, f.n_sellers, f.revenue, f.freight, f.distance_km, f.same_state,
               c.state AS customer_state
        FROM fact_orders f JOIN dim_customer c USING (customer_id)
        WHERE f.in_window = 1 AND f.is_delivered = 1 AND f.chronology_error = 0 AND f.n_items > 0""", con,
        parse_dates=["purchase_ts", "approved_ts", "delivered_ts"])
    items = pd.read_sql("""
        SELECT i.order_id, i.seller_id, i.price, i.shipping_limit_ts, s.state AS seller_state,
               p.category, p.weight_g, p.volume_cm3
        FROM fact_order_items i JOIN dim_seller s USING (seller_id) JOIN dim_product p USING (product_id)""",
        con, parse_dates=["shipping_limit_ts"])
    return o, items


def add_features(o, items):
    # Main seller / category = the most expensive item in the order.
    main = items.sort_values("price", ascending=False).drop_duplicates("order_id")
    agg = items.groupby("order_id").agg(weight_g=("weight_g", "sum"), volume_cm3=("volume_cm3", "sum"),
                                        shipping_limit_ts=("shipping_limit_ts", "min"))
    o = o.merge(main[["order_id", "seller_id", "seller_state", "category"]], on="order_id", how="left")
    o = o.merge(agg, on="order_id", how="left")

    o["freight_ratio"] = o.freight / o.revenue
    o["purchase_dow"] = o.purchase_ts.dt.dayofweek
    o["purchase_hour"] = o.purchase_ts.dt.hour
    o["purchase_month_num"] = o.purchase_ts.dt.month
    o["approval_hours"] = (o.approved_ts - o.purchase_ts).dt.total_seconds() / 3600
    o["handover_window_days"] = (o.shipping_limit_ts - o.approved_ts).dt.total_seconds() / 86400

    # Seller history known at purchase: outcomes of the seller's orders delivered BEFORE this purchase.
    hist = o[["seller_id", "delivered_ts", "is_late"]].sort_values("delivered_ts").copy()
    hist["prior_n"] = hist.groupby("seller_id").cumcount() + 1
    hist["prior_late"] = hist.groupby("seller_id").is_late.cumsum()
    q = o[["order_id", "seller_id", "purchase_ts"]].sort_values("purchase_ts")
    m = pd.merge_asof(q, hist[["seller_id", "delivered_ts", "prior_n", "prior_late"]],
                      left_on="purchase_ts", right_on="delivered_ts", by="seller_id",
                      direction="backward", allow_exact_matches=False)
    o = o.merge(m[["order_id", "prior_n", "prior_late"]], on="order_id", how="left")
    o["seller_prior_orders"] = o.prior_n.fillna(0)
    # Smoothed late rate: shrink towards the overall rate (~6%) when history is short.
    o["seller_prior_late_rate"] = (o.prior_late.fillna(0) + 0.06 * 10) / (o.seller_prior_orders + 10)

    # Market load known at purchase: orders placed in the previous 7 days, late rate of deliveries in the previous 14 days.
    daily_buy = o.set_index("purchase_ts").sort_index().order_id.resample("D").count()
    load7 = daily_buy.rolling(7, min_periods=1).sum().shift(1)
    o["orders_last_7d"] = o.purchase_ts.dt.floor("D").map(load7).fillna(0)
    dl = o.set_index("delivered_ts").sort_index().is_late.resample("D").agg(["sum", "count"])
    roll = dl.rolling(14, min_periods=1).sum().shift(1)
    rate14 = (roll["sum"] / roll["count"]).rename("rate")
    o["market_late_rate_14d"] = o.purchase_ts.dt.floor("D").map(rate14)
    return o


NUM = ["promised_days", "n_items", "n_sellers", "revenue", "freight", "freight_ratio", "distance_km", "same_state",
       "weight_g", "volume_cm3", "purchase_dow", "purchase_hour", "purchase_month_num", "approval_hours",
       "handover_window_days", "seller_prior_orders", "seller_prior_late_rate", "orders_last_7d",
       "market_late_rate_14d"]
CAT = ["customer_state", "seller_state", "category"]


def recall_at(y, score, top=0.10):
    k = int(len(y) * top)
    idx = np.argsort(-score)[:k]
    return y[idx].sum() / y.sum(), y[idx].mean()


def evaluate(name, y, score):
    r, p = recall_at(y, score)
    return {"model": name, "pr_auc": average_precision_score(y, score), "roc_auc": roc_auc_score(y, score),
            "recall_top10": r, "precision_top10": p}


def main():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(os.path.join(ROOT, "data", "processed", "olist.db"))
    o = add_features(*load(con))
    train, test = o[o.purchase_month < TEST_FROM].copy(), o[o.purchase_month >= TEST_FROM].copy()
    ytr, yte = train.is_late.values, test.is_late.values
    print(f"Train {len(train):,} orders (late {ytr.mean():.1%}) | Test {len(test):,} orders (late {yte.mean():.1%})")

    results = [evaluate("Random (base rate)", yte, np.random.default_rng(SEED).random(len(yte))),
               evaluate("Rule: seller prior late rate", yte, test.seller_prior_late_rate.values)]

    # Logistic regression on numeric features (median-imputed).
    med = train[NUM].median()
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced"))
    lr.fit(train[NUM].fillna(med), ytr)
    p_lr = lr.predict_proba(test[NUM].fillna(med))[:, 1]
    results.append(evaluate("Logistic regression", yte, p_lr))

    # LightGBM with categorical features.
    for c in CAT:
        cats = pd.CategoricalDtype(sorted(train[c].dropna().unique()))
        train[c] = train[c].astype(cats)
        test[c] = test[c].astype(cats)
    gbm = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.03, num_leaves=31, min_child_samples=50,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1)
    gbm.fit(train[NUM + CAT], ytr)
    p_gbm = gbm.predict_proba(test[NUM + CAT])[:, 1]
    results.append(evaluate("LightGBM", yte, p_gbm))

    res = pd.DataFrame(results).set_index("model")
    print("\nTest metrics (Apr–Aug 2018):\n", res.round(3).to_string())
    res.to_csv(f"{OUT}/metrics.csv")

    # By-month recall to check stability.
    test["score"] = p_gbm
    print("\nLightGBM recall@top10% by test month:")
    for mth, g in test.groupby("purchase_month"):
        r, p = recall_at(g.is_late.values, g.score.values)
        print(f"  {mth}: late {g.is_late.mean():.1%}, recall {r:.1%}, precision {p:.1%}")

    sv = shap.TreeExplainer(gbm).shap_values(test[NUM + CAT])
    sv = sv[1] if isinstance(sv, list) else sv
    imp = pd.Series(np.abs(sv).mean(axis=0), index=NUM + CAT).sort_values(ascending=False)
    print("\nMean |SHAP| (top 10):\n", imp.head(10).round(4).to_string())
    imp.to_csv(f"{OUT}/shap_importance.csv", header=["mean_abs_shap"])
    test[["order_id", "purchase_month", "is_late", "score", "seller_prior_late_rate"]].to_csv(
        f"{OUT}/scores_test.csv", index=False)


if __name__ == "__main__":
    main()
