# WS4 — Recommendation, FRD and Pilot Plan

## Recommendation (BQ9)

**Fix the promise and the sellers first; do not build the early-warning system at today's volume.**

| Option | Year-1 result | Decision |
|---|---|---|
| A. Route-calibrated ETA | Not modelled in money (needs conversion data); attacks the main cause: transit (+19.9 days on late orders) and an ETA buffer that does not fit each state (correlation −0.72) | **Build — pilot first** |
| B. Seller handover SLA (Tier A/B/C) | Not modelled in money; late handover lifts late rate 5.4% → 21.1% | **Build — staged rollout** |
| C. Early warning + proactive message | Base scenario **−R$ 40,528** in year 1; break-even needs a save rate of 289% (impossible) or **12.7× today's volume** | **Park** — revisit if real volume is 13× the dataset |

Source: `reports/excel/business_case.xlsx` (Model and Sensitivity sheets). The model is weak because the money levers are small: a saved late order avoids 0.54 low reviews, and repeat purchase rises by only 0.51 percentage points (3.03% vs 2.52%).

---

## FRD — Delivery Promise and Seller SLA

### Functional requirements

| ID | Requirement | Story | Priority |
|---|---|---|---|
| FR-01 | Compute the promised delivery date from a route table (seller state × customer state × distance band) that holds the 85th-percentile transit time from the last 90 days | US-03, US-05 | Must |
| FR-02 | Recalculate the route table every week; routes with fewer than 30 orders fall back to the state-to-state value | US-03 | Must |
| FR-03 | Show the promise to the customer at checkout and in the confirmation message | US-03 | Must |
| FR-04 | Calculate each seller's handover-late rate and average review weekly; assign Tier A / B / C with the thresholds on the scorecard's Settings sheet | US-04 | Must |
| FR-05 | Send Tier B sellers a coaching message; Tier C sellers get an account review and a 30-day improvement plan before any penalty | US-04 | Must |
| FR-06 | Operations dashboard: late rate by route and week, tier changes, sellers entering Tier C | US-01, US-03 | Should |
| FR-07 | Log the route table version and tier used for every order, so the pilot can be analysed | US-10 | Must |
| FR-08 | (Phase 2, if Option C is revived) Score each order at approval with the logistic-regression model and message the top 10% | US-08 | Could |

### Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | Route table and tiers refresh weekly, by Monday 06:00 |
| NFR-02 | ETA calculation adds less than 100 ms to checkout |
| NFR-03 | Customer location used only at state / zip-prefix level (LGPD data minimisation) |
| NFR-04 | Seller tier is visible to the seller with the numbers behind it (fairness, dispute process) |
| NFR-05 | Every number on the dashboard matches the SQL validation queries within 0.1% |

### To-Be process

1. Customer checks out → **route table gives the promise** (FR-01) → promise shown (FR-03).
2. Payment approved → seller notified with the handover deadline.
3. Seller hands over → **handover logged against the deadline** (FR-04).
4. Carrier delivers → delivery logged against the promise.
5. Weekly → route table refreshed (FR-02), tiers recalculated (FR-04), coaching / reviews sent (FR-05), dashboard updated (FR-06).

Change from As-Is: the promise moves from one buffer for all routes to a buffer per route, and seller handover becomes a managed KPI instead of an unreported one.

### Wireframes to draw in Figma (D39)
1. **Seller portal — "Your delivery score"**: tier badge, handover-late rate vs threshold, trend for 12 weeks, the 5 latest late handovers, "How to improve" tips.
2. **Operations dashboard — "Routes this week"**: map by customer state coloured by late rate, table of the 10 worst routes with old vs new promise, list of sellers entering Tier C.

---

## Pilot plan (Option A)

| Item | Plan |
|---|---|
| Design | Randomised A/B by order: 50% get the route-calibrated promise (treatment), 50% the current promise (control) |
| Primary metric | Late delivery rate (KPI 7) |
| Secondary metric | Average review score (KPI 4) |
| Guardrail | Checkout conversion must not fall by more than 1 percentage point; longer promises can cost sales, and this data cannot measure that |
| Sample size | Baseline late rate 7.8% (last 12 months). To detect a 20% relative drop (7.8% → 6.2%) at 95% confidence and 80% power: **4,219 orders per arm, 8,438 in total** |
| Duration | About **1.4 months** at this dataset's volume (~6,170 delivered orders per month); run 6 weeks to cover full weeks and avoid peak months (November, February–March) |
| Decision rule | Roll out if late rate falls significantly and the guardrail holds; otherwise keep the current promise and retest with a different percentile |

Option B is rolled out in stages (coaching only for 4 weeks, then reviews), not A/B tested: treating comparable sellers differently on purpose would be unfair.
