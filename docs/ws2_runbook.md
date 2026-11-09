# WS2 Runbook — Voice of Customer with a Local LLM

Runs on your own machine with LM Studio. Review text never leaves the machine (point to make to Data Privacy).

**Scope:** 9,195 low reviews (1–2★) with a comment, delivered orders in the analysis window: 2,745 from late orders, 6,450 from on-time orders.

| Day | Step | Command / action | Output |
|---|---|---|---|
| D20 | Draw the sample | `python src/ws2_sample.py` | `label_sample.csv`: 200 reviews, 100 late + 100 on time |
| D21–22 | Label by hand | Open the CSV in Excel, fill `human_label` using [ws2_taxonomy.md](ws2_taxonomy.md). Use a translator for Portuguese if needed. Note doubts in `notes` | 200 human labels |
| D23 | Validate the LLM | Start LM Studio server → `python src/ws2_classify.py --model <id>` → `python src/ws2_evaluate.py data/processed/ws2/label_sample_llm.csv` | Macro-F1 (KPI 16). Bar: 0.70 |
| D23 | Improve if below bar | Read the confusion matrix, add rules or examples to `SYSTEM` in `ws2_classify.py`, rerun | Prompt v2 + new F1 |
| D24 | Classify everything | `python src/ws2_classify.py --input data/processed/ws2/low_reviews_all.csv --model <id>` (resumes if stopped) | `low_reviews_all_llm.csv` |
| D24 | Summarise | `python src/ws2_evaluate.py data/processed/ws2/low_reviews_all_llm.csv --summary` | KPI 15 by delivery status and by seller count |
| D24 | Power BI | Load `low_reviews_all_llm.csv`, relate on `order_id`, build page *Why Customers Complain* | US-09 |

## Hypotheses to test (from WS1)
1. On-time low reviews are mostly product problems (`damaged_defective`, `quality_not_as_described`, `wrong_item`).
2. Multi-seller orders (47% low-review rate vs 12%) show many `partial_or_missing` complaints: items arrive separately and customers think part of the order is lost.
3. Some "on-time" complaints are actually `not_delivered`, which would mean the delivery date in the data is wrong for those orders.

## What to write in the findings
- Macro-F1, the two most-confused labels and what you changed in the prompt.
- Top 3 complaint categories for late and for on-time orders, with %.
- Whether hypothesis 2 holds; it decides whether WS4 adds a "your order ships in parts" message.
