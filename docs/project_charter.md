# Project Charter: Olist Delivery Intelligence

| | |
|---|---|
| Project owner and analyst | Maetasit Pittatanang |
| Sponsor and approver (simulated) | Head of Operations |
| Version | 1.0 (Gate D5) |
| Status | Approved (simulated sponsor sign-off) |

> Portfolio project on real public data. The sponsor, budget and stakeholders are simulated; the BRD (v0.2) and RACI hold the detail.

## 1. Problem

Olist customers give an average of 4.16 stars, but late orders average 2.27 against 4.29 for on-time orders. Promised delivery dates are padded by about 12 days, yet 6.8% of orders still arrive late. Two in three low reviews come from orders that arrived on time, so delivery speed alone does not explain dissatisfaction.

## 2. Objectives

1. Find where in the order journey delay happens and why (WS1).
2. Find what unhappy customers actually complain about (WS2).
3. Test whether late orders can be flagged at payment approval (WS3).
4. Recommend the fix that pays back first, with a costed pilot (WS4).

## 3. Scope

| In scope | Out of scope |
|---|---|
| Orders Jan 2017 – Aug 2018 (99,092 orders) | Live system changes or integration |
| Delivery stages, review scores and review text | Payments fraud, pricing and marketing |
| Seller, carrier and route (state) analysis | Individual seller or customer outreach |
| Business case, FRD, pilot design | Running the pilot itself |

## 4. Deliverables

| Workstream | Deliverable |
|---|---|
| WS0 Data Foundation | SQLite star schema, data-quality tests, cleaning log, data dictionary |
| WS1 Diagnose | Power BI report, process mining, driver tree, findings |
| WS2 Voice of Customer | Complaint taxonomy, labelled sample, classifier, findings |
| WS3 Predict | Late-delivery risk model, model card |
| WS4 Design and Prove | Excel business case, seller scorecard, FRD, To-Be process, wireframes, pilot plan |
| Communication | Executive deck, README, 3-minute video |

## 5. Success criteria

| Criterion | Target |
|---|---|
| Data-quality tests passing | 100% |
| Complaint classifier accuracy | Macro-F1 ≥ 0.70 on held-out labels |
| Risk model | Beats the seller-history rule on recall at top 10% |
| Recommendation | Costed, with break-even and a pilot sample size |
| Every assumption | Labelled as real data or simulated |

## 6. Milestones and gates

| Gate | Day | Exit condition |
|---|---|---|
| G1 Charter signed | D5 | This document approved |
| G2 Data trusted | D10 | Data-quality tests pass |
| G3 Diagnosis agreed | D30 | WS1 and WS2 findings reviewed |
| G4 Recommendation | D45 | Business case and pilot plan ready |
| G5 Portfolio live | D50 | Repo public, video and post published |

## 7. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Data is 2016–2018 only | Findings may not reflect today's operation | State the period on every chart; recommend a pilot before rollout |
| No real cost data | Business case could mislead | Scenario and sensitivity analysis; assumptions labelled |
| Review text is Portuguese | Labelling errors | Taxonomy with Portuguese cues; held-out accuracy test |
| Model leakage | Over-optimistic results | Time-based split; features only known at approval |
| Scope creep | Project never finishes | Gates G1–G5; MoSCoW priorities in the BRD |

## 8. Stakeholders (simulated)

Head of Operations (sponsor, approves), CX Lead, Logistics, Seller Account Management, BI / Data, Engineering / IT, Finance. Roles are in the RACI (D3): the BA is Responsible and the Head of Operations is Accountable for this charter.

## 9. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Business Analyst (R) | Maetasit Pittatanang | Submitted | 2026-11-09 |
| Head of Operations (A, simulated) | — | Approved, simulated for this portfolio project | 2026-11-09 |
| CX Lead, Logistics, BI / Data (C, simulated) | — | Consulted, simulated | 2026-11-09 |
