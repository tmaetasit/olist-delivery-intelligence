"""WS1 process mining on order timestamps with pm4py.

Usage:  python src/ws1_process_mining.py
Builds an event log (one case per delivered order, analysis window), then reports
process variants and the mean time between activities for on-time vs late orders.
"""
import os
import sqlite3

import pandas as pd
import pm4py

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVITIES = [("purchase_ts", "1 Order placed"), ("approved_ts", "2 Payment approved"),
              ("carrier_ts", "3 Handed to carrier"), ("delivered_ts", "4 Delivered")]


def main():
    con = sqlite3.connect(os.path.join(ROOT, "data", "processed", "olist.db"))
    o = pd.read_sql("""SELECT order_id, is_late, purchase_ts, approved_ts, carrier_ts, delivered_ts
                       FROM fact_orders WHERE in_window = 1 AND is_delivered = 1""", con)
    events = []
    for col, name in ACTIVITIES:
        e = o[["order_id", "is_late", col]].dropna().rename(columns={col: "timestamp"})
        e["activity"] = name
        events.append(e)
    log = pd.concat(events)
    log["timestamp"] = pd.to_datetime(log["timestamp"])
    log = pm4py.format_dataframe(log, case_id="order_id", activity_key="activity", timestamp_key="timestamp")
    print(f"Event log: {log['case:concept:name'].nunique():,} cases, {len(log):,} events")

    variants = pm4py.get_variants(log)
    total = sum(variants.values())
    print("\nProcess variants (order of activities by timestamp):")
    for v, n in sorted(variants.items(), key=lambda x: -x[1])[:6]:
        print(f"  {n:>7,}  {n / total:6.2%}  {' -> '.join(v)}")

    print("\nMean hours between activities (performance DFG):")
    for label, part in [("on time", 0), ("late", 1)]:
        sub = log[log["is_late"] == part]
        dfg, _, _ = pm4py.discover_performance_dfg(sub)
        rows = {f"{a} -> {b}": d["mean"] / 3600 for (a, b), d in dfg.items()}
        print(f"\n  {label}:")
        for k in sorted(rows):
            print(f"    {k:45s} {rows[k]:8.1f} h  ({rows[k] / 24:5.1f} days)")


if __name__ == "__main__":
    main()
