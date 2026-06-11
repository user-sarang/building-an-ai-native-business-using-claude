# Marketing Reporting Spec — abc

Defines what the downstream marketing-head agent produces at each cadence and exactly which sheets/columns it reads. Daily / weekly / monthly are **rollups computed from the daily `mkt-ad-performance` rows and per-event `mkt-influencer-collabs` rows** — nothing here is hand-stored.

## Source data
- `trackers/mkt-campaigns/` — campaign list, budgets, targets
- `trackers/mkt-ad-performance/` — daily paid rows (Meta / Google / Amazon)
- `trackers/mkt-influencer-collabs/` — per-collab rows (when the channel goes live)
- `trackers/sales-d2c-orders/` — true revenue, joined via `utm_campaign` ↔ `coupon_code` / UTM

## Computed metrics
CTR = clicks/impressions · CPC = spend/clicks · CPM = spend/impressions×1000 · CAC = spend/conversions · ROAS = conversion_value/spend · conversion rate = conversions/clicks · spend pacing vs budget.

## abc's KPI targets (the headline numbers)
| Metric | Target | Primary cadence |
|---|---|---|
| ROAS | 3.0× | daily pacing + weekly |
| CAC | ≤ ₹1,500 (confirm) | weekly |
| CTR | ≥ 1.5% | daily / weekly |
| Conversion rate | baseline TBD | weekly |

## Daily report — pacing + anomalies
Audience: Sandeep (performance marketer). Purpose: catch problems same-day, tee up bid changes.
Show:
- Yesterday's spend, conversions, revenue, ROAS by campaign and platform.
- Pacing: month-to-date spend vs `total_budget` (and vs the <₹50k/mo total).
- Flags: any campaign with ROAS below its `target_value`; CPC/CPM spiking vs 7-day average; CTR below 1.5%; a creative concept whose performance dropped.
- Output: short table + a 3–5 bullet "what to change today" list.
- Written to `reports/marketing/daily/YYYY-MM-DD.*`.

## Weekly report — review + creative learnings
Audience: Sandeep + founder. Purpose: reallocation decisions.
Show:
- Week-over-week spend, revenue, blended ROAS, CAC by channel (Meta / Google / Amazon).
- Top and bottom campaigns vs target.
- Creative leaderboard: best/worst `concept` & `variant` by ROAS (join `creatives-index` → `mkt-ad-performance` on `utm_campaign` + ad-set).
- Any influencer collabs that went live and their attributed orders (once that channel is active).
- Output: 1-page summary with a reallocation recommendation.
- Written to `reports/marketing/weekly/YYYY-Www.*`.

## Monthly report — the board number
Audience: founder / leadership. Purpose: the headline.
Show:
- Total marketing spend, total attributed revenue, blended ROAS and CAC for the month.
- Spend mix and ROAS by channel; trend vs prior months.
- Campaign scorecard: each campaign's `target_metric` target vs actual.
- Output: a clean exec summary suitable for a leadership review.
- Written to `reports/marketing/monthly/YYYY-MM.*`.
