# reporting-spec.md — template

Defines what the downstream marketing-head agent must produce at each cadence, and exactly which sheets
and columns it reads. Remember: daily/weekly/monthly are **rollups computed from the daily ad-performance
rows and per-event influencer rows** — nothing here is hand-stored. Tailor the KPI list to the user's
Phase 9 answers.

```markdown
# Marketing Reporting Spec

Source data:
- mkt-campaigns (campaign list, budgets, targets)
- mkt-ad-performance (daily paid rows)
- mkt-influencer-collabs (per-collab rows)
- sales-d2c-orders (true revenue, joined via utm_campaign / promo_code) — if present

Computed metrics: CTR, CPC, CPM, CAC, ROAS, conversion rate, spend pacing vs budget.

## Daily report (pacing + anomalies)
Audience: the marketer. Purpose: catch problems same-day, tee up bid changes.
Show:
- Yesterday's spend, conversions, revenue, ROAS by campaign and platform.
- Pacing: spend-to-date vs total_budget × (days elapsed / campaign length).
- Flags: any campaign with ROAS below target, CPC/CPM spiking vs 7-day average, or a creative whose
  performance dropped — candidates for bid/budget adjustment.
- Output: short table + a 3–5 bullet "what to change today" list.

## Weekly report (review + creative learnings)
Audience: marketer + founder. Purpose: reallocation decisions.
Show:
- Week-over-week spend, revenue, blended ROAS, CAC by channel.
- Top and bottom campaigns vs target.
- Creative leaderboard: best/worst concept & variant by ROAS (join creatives-index → ad-performance).
- Influencer collabs that went live this week and their attributed orders.
- Output: 1-page summary with a reallocation recommendation.

## Monthly report (the board number)
Audience: founder / leadership. Purpose: the headline.
Show:
- Total marketing spend, total attributed revenue, blended ROAS and CAC for the month.
- Spend mix and ROAS by channel; trend vs prior months.
- Campaign scorecard: each campaign's target vs actual.
- Output: a clean exec summary suitable for a leadership review.
```

The agent writes daily reports to `reports/daily/YYYY-MM-DD.*`, weekly to `reports/weekly/YYYY-Www.*`,
monthly to `reports/monthly/YYYY-MM.*`.
