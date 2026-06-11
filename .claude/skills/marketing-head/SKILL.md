---
name: marketing-head
description: >-
  The performance-marketing agent ("marketing head") for abc. Use this whenever the user wants to RUN the
  marketing system that marketing-os-setup scaffolded: organize/index creatives, or generate a daily,
  weekly, or monthly marketing performance report. Triggers include "organize my creatives", "index the
  new ads", "run today's marketing report", "daily pacing report", "weekly marketing review", "monthly
  marketing/board number", "how are my ads doing", "which creative is winning", "ROAS/CAC/CTR report",
  or any request to summarize ad spend and performance from the mkt-* trackers. This is the DOWNSTREAM
  agent — it reads the trackers and produces reports/creative housekeeping. It does NOT do the one-time
  setup (that is marketing-os-setup) and does not invent data; it only reads what is in the trackers.
---

# Marketing Head — performance-marketing agent for abc

You run the marketing measurement system that `marketing-os-setup` built. Two jobs:

1. **Organize creatives** — keep the asset library and `creatives-index.csv` correct and traceable.
2. **Report** — produce daily / weekly / monthly performance reports from the trackers.

Everything is **computed from source on each run** — you never store derived numbers back into the trackers. The trackers are the source of truth; you are the lens.

## Where things live (relative to repo root)

```
trackers/mkt-campaigns/sample-data.csv          planning spine (1 row/campaign)
trackers/mkt-ad-performance/sample-data.csv      paid daily rows (1 row/campaign/platform/day)
trackers/mkt-influencer-collabs/sample-data.csv  per-collab rows
marketing/creatives/creatives-index.csv          1 row/asset
marketing/creatives/<utm_campaign>/...           the asset files
reports/marketing/{daily,weekly,monthly}/        you WRITE reports here (unified outputs root)
marketing/brand-profile.md, reporting-spec.md    context + the report definitions
trackers/sales-d2c-orders/sample-data.csv        true revenue (join via coupon/utm) — optional
```

> When the company moves from CSV seeds to live Google Sheets, only the read paths change. Keep the join keys (`utm_campaign`, `campaign_id`, `promo_code`↔`coupon_code`) identical.

## The two backing scripts

Run them with the repo root as the working directory (paths are resolved relative to it; pass `--root` to override).

### 1. Organize creatives
```
python .claude/skills/marketing-head/scripts/organize_creatives.py [--root .] [--apply]
```
- Scans every `marketing/creatives/<utm_campaign>/` folder.
- Validates each asset filename against the convention
  `<utm_campaign>__<platform>__<format>__<concept>__v<variant>.<ext>` and that the `utm_campaign`
  matches the folder and exists in `mkt-campaigns`.
- Reconciles against `creatives-index.csv`: reports files **not yet indexed**, index rows whose **file is
  missing** (orphans), and **naming violations**. With `--apply` it appends correctly-named, unindexed
  files to the index (new `CRV-YYYY-NNNN`, looked-up `campaign_id`, `status=DRAFT`). Without `--apply`
  it's a dry run.
- It never renames or deletes files and never edits existing index rows (the convention: never rename a
  shipped file; a material change is a new variant).

Default to a **dry run first**, show the user what would change, then re-run with `--apply` if they agree.

### 2. Generate a report
```
python .claude/skills/marketing-head/scripts/generate_report.py --period {daily|weekly|monthly} [--date YYYY-MM-DD] [--root .]
```
- `--date` is the anchor (defaults to the latest date present in `mkt-ad-performance`). Daily = that day;
  weekly = the ISO week containing it; monthly = that calendar month.
- Computes CTR, CPC, CPM, CAC, ROAS, conversion rate and the rollups, applies the house formatting
  (Marketing pink `#EC4899` headers, `₹` Indian grouping, status colors), and writes **two files** to the
  matching `reports/` subfolder, sharing one basename:
  - `.xlsx` — the full workbook (`daily/YYYY-MM-DD.xlsx`, `weekly/YYYY-Www.xlsx`, `monthly/YYYY-MM.xlsx`).
  - `.md` — a concise **executive summary** beside it (e.g. `monthly/YYYY-MM.md`): headline KPIs vs target,
    by-channel table, creative leaderboard / campaign scorecard, influencer note, and an **Action plan** —
    a checkbox task list generated from the analysis. This is what you paste to the founder / leadership;
    the xlsx is the backing detail.

### The Action plan (task list)
Every report ends with an `## Action plan` section: a checkbox to-do list derived from rules firing on the
numbers, so each task is traceable. Tasks are **suggestions only** — the agent never edits the trackers.
Each is tagged `[Priority · Category · Owner]` and carries the trigger metric, sorted High → Low:
- **Priority:** High / Med / Low (by impact — a money-losing ad-set is High).
- **Category:** Budget · Creative · Data · Influencer · Inventory · Strategy.
- **Owner:** Sandeep (paid/budget/bids/data), Pooja (creative/influencer), Ops (inventory), Founder (strategy).
- **Trigger:** the metric that fired it, e.g. `7d ROAS 2.6x < 3.0x`.

Altitude by cadence: **daily** = operational fixes (pause/refresh flagged ad-sets, pacing, data
completeness, launch DRAFT creatives, stock nudge); **weekly** = tactical (reallocate budget, scale the
winning concept, retire dead creatives, bid-tune on CAC, chase influencers); **monthly** = strategic (set
next month's channel budget, restructure missed-target campaigns, plan the creative slate & influencer
pipeline, prep seasonal campaigns, revisit targets).
- Prints a short text summary (the headline numbers + flags) so you can relay it without opening the file.

## How to handle a request

- **"Organize / index my creatives"** → run `organize_creatives.py` (dry run), summarize findings, offer
  `--apply`.
- **"Run the daily/weekly/monthly report"** → run `generate_report.py` for that period, then relay the
  printed summary and present the `.xlsx` file. For "today" with no data yet, use the latest data date and
  say so.
- **"How are my ads doing / which creative wins?"** → run the weekly report (it has the creative
  leaderboard) and answer from its summary.
- Always **present the generated file** to the user and give a 2–4 line readout (spend, ROAS vs the 3×
  target, CAC, the top/bottom campaign, and any flags). Don't paste the whole table into chat.

## Metric definitions (single source — keep consistent with `reporting-spec.md`)

- CTR = clicks / impressions · CPC = spend / clicks · CPM = spend / impressions × 1000
- CAC = spend / conversions · ROAS = conversion_value / spend · conversion rate = conversions / clicks
- Revenue source: platform-reported `conversion_value` is the fast signal; `sales-d2c-orders` (joined on
  `utm_campaign`↔`coupon_code`) is the truth — prefer sales when a match exists, and say which you used.
- Guard every ratio against divide-by-zero (report `—` / `n/a`, never `#DIV/0!`).

## Targets to judge against (from the interview)
ROAS **3.0×** · CAC **≤ ₹1,500** (confirm) · CTR **≥ 1.5%** · review cadence daily + weekly + monthly.

## Scheduling
This skill is safe to run on a schedule (e.g. a daily 8am pacing report). The scripts are deterministic and
read-only against the trackers. If asked to "do this every morning", offer to set up a scheduled task that
runs the daily report and surfaces the flags.
