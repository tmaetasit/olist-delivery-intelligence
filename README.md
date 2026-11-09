# Olist Delivery Intelligence

**Why do customers leave bad reviews, which orders will arrive late before they do, and which fix pays back first?**

An end-to-end Business Analyst case study on the public [Brazilian E-Commerce dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): 1.55 million rows across 9 tables, covering ~100k orders from 2016–2018.

> Portfolio project. The data is real. The stakeholders, costs and pilot are simulated, and every assumption is labelled.

---

## Early findings (D1 data profile)

| Signal | Value | Why it matters |
|---|---|---|
| Average review score: late vs on-time orders | **2.27 vs 4.29** | Delay hurts satisfaction badly |
| Low reviews (1–2★): late vs on-time orders | **62% vs 9%** | Late orders are ~7× more likely to get a bad review |
| Share of low reviews caused by late orders | **33%** | **Two in three bad reviews come from on-time orders**, so delivery is not the whole story |
| Promised vs actual delivery time | **24.3 vs 12.5 days** | ETAs are padded by ~12 days, yet 6.8% of orders still arrive late |
| Repeat customers | **3.1%** | A business case cannot rest on repeat purchases alone |

Analysis window: Jan 2017 – Aug 2018 (99,092 orders; 96,203 delivered).

---

## Approach

| Workstream | Question | Methods and tools |
|---|---|---|
| WS0 Data Foundation | Can we trust the data? | SQL layers (raw → staging → mart), data quality tests, star schema |
| WS1 Diagnose | Where and why does delay happen? | Power BI + DAX, process mining (pm4py), root-cause driver tree |
| WS2 Voice of Customer | What do unhappy customers complain about? | LLM review classification (local, LM Studio), validated on 200 human labels |
| WS3 Predict | Can we see a late order coming at payment approval? | scikit-learn / LightGBM, SHAP, compared with a simple seller-history rule |
| WS4 Design and Prove | What should we build, and does it pay back? | Excel business case (scenarios, sensitivity, break-even), FRD, Figma wireframe, pilot A/B design |

Business analysis artefacts: BRD v0.2, KPI dictionary (18 KPIs), 10 user stories with acceptance criteria, stakeholder map and RACI.

---

## Repository structure

```
data/raw/          Olist CSV files (not committed; see "Reproduce")
sql/01_raw/        Load raw tables into SQLite
sql/02_staging/    Typed, de-duplicated, translated tables
sql/03_mart/       Star schema: fact_orders, fact_order_items, dim_*
sql/tests/         Data quality tests
src/               Python scripts (profiling, features, LLM labelling)
notebooks/         Process mining and model notebooks
reports/powerbi/   Power BI report (.pbix)
reports/excel/     Seller scorecard and business case
design/            Process maps and wireframes
docs/              BRD, KPI dictionary, data profile, model card
```

---

## Reproduce

1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and put the 9 CSV files in `data/raw/`.
2. Install Python packages: `pip install -r requirements.txt`
3. Run the data profile: `python src/d1_profile.py data/raw`

---

## Status

- [x] D1 Data profile
- [x] D2 BRD v0.2
- [x] D3 Stakeholder map and RACI
- [x] D4 Repository set-up
- [ ] WS0 Data foundation (weeks 2–3)
- [ ] WS1 Diagnose (weeks 3–4)
- [ ] WS2 Voice of customer (weeks 4–5)
- [ ] WS3 Predict (weeks 5–7)
- [ ] WS4 Design and prove (weeks 8–9)
- [ ] Executive deck and video (week 10)

---

## How AI was used

- Claude helped plan the project, draft documents and write and debug code. Every query, measure and number was reviewed and can be explained by the author.
- A local LLM (LM Studio) classifies review text in WS2, so review data never leaves the machine. Its accuracy is measured against human labels before results are used.

---

## Data and licence

Data: Olist, via Kaggle; see the dataset page for its licence terms. This repository contains analysis code and documents only, not the raw data.

**Author:** Maetasit Pittatanang · Business Analyst
