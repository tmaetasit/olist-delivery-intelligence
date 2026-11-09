"""WS2 step 3: compare LLM labels with human labels, then summarise all complaints.

Usage:
  python src/ws2_evaluate.py data/processed/ws2/label_sample_llm.csv        # KPI 16: Macro-F1
  python src/ws2_evaluate.py data/processed/ws2/low_reviews_all_llm.csv --summary   # KPI 15
"""
import argparse

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score

BAR = 0.70


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--summary", action="store_true")
    a = p.parse_args()
    df = pd.read_csv(a.file)

    if a.summary:
        t = pd.crosstab(df.llm_label, df.is_late.map({0: "on time", 1: "late"}), normalize="columns")
        print("Complaint Category Share (KPI 15) by delivery status:\n", (t * 100).round(1).to_string())
        m = pd.crosstab(df.llm_label, df.n_sellers > 1, normalize="columns")
        print("\nShare by one seller (False) vs several sellers (True):\n", (m * 100).round(1).to_string())
        return

    df = df[df.human_label.fillna("").str.strip() != ""]
    y, yhat = df.human_label.str.strip(), df.llm_label
    f1 = f1_score(y, yhat, average="macro")
    print(f"Labelled rows: {len(df)}  Macro-F1 (KPI 16): {f1:.3f}  -> {'PASS' if f1 >= BAR else 'BELOW BAR'} ({BAR})")
    print(classification_report(y, yhat, zero_division=0))
    labels = sorted(set(y) | set(yhat))
    print(pd.DataFrame(confusion_matrix(y, yhat, labels=labels), index=labels, columns=labels).to_string())


if __name__ == "__main__":
    main()
