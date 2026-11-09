"""WS2 step 1: draw 200 low reviews with comments for human labelling.

Usage:  python src/ws2_sample.py
Output: data/processed/ws2/label_sample.csv  (fill in the human_label column)
        data/processed/ws2/low_reviews_all.csv (every commented low review, for the LLM)
"""
import os
import sqlite3

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "processed", "ws2")

QUERY = """
SELECT f.order_id, f.is_late, f.n_items, f.n_sellers, r.review_score, r.review_comment_message AS comment
FROM fact_orders f
JOIN stg_reviews r USING (order_id)
WHERE f.in_window = 1 AND f.is_delivered = 1 AND f.is_low_review = 1 AND r.has_comment = 1
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(os.path.join(ROOT, "data", "processed", "olist.db"))
    df = pd.read_sql(QUERY, con)
    df["comment"] = df.comment.str.replace(r"\s+", " ", regex=True).str.strip()
    df.to_csv(os.path.join(OUT, "low_reviews_all.csv"), index=False)

    # Stratify so both late and on-time complaints are well represented (100 each).
    sample = df.groupby("is_late").sample(n=100, random_state=42)
    sample = sample.sample(frac=1, random_state=42)          # shuffle so labellers don't see the split
    sample["human_label"] = ""
    sample["notes"] = ""
    sample.to_csv(os.path.join(OUT, "label_sample.csv"), index=False)
    print(f"Commented low reviews: {len(df):,} (late {df.is_late.sum():,}, on time {(df.is_late == 0).sum():,})")
    print(f"Sample written: {len(sample)} rows -> {os.path.relpath(OUT, ROOT)}/label_sample.csv")


if __name__ == "__main__":
    main()
