# Tracker schemas — exact specs

The marketing measurement system is **three layers joined by `campaign_id` + `utm_campaign`**:

```
mkt-campaigns            planning spine    1 row per initiative (spans weeks)
   ├─ mkt-ad-performance paid measurement  1 row per campaign · platform · DAY
   └─ mkt-influencer-collabs influencer    1 row per collab/post (an event)
creatives-index          asset library     1 row per creative file
```

Apply the Design Bible to all of them: prefixed immutable IDs, `YYYY-MM-DD` dates, snake_case headers,
SCREAMING_SNAKE enums, soft delete via `is_active`/`status`, Marketing header color Pink `#EC4899`.
Derived metrics (ROAS, CAC, CTR, CPM, CPC, conversion rate, weekly/monthly totals) are **not stored** —
the downstream agent computes them. Each schema.md should list those under a "What's NOT stored (computed
on the fly)" section, mirroring the other trackers in this repo.

---

## 1. `mkt-campaigns` (master / planning — channel-agnostic)

One row per campaign initiative. Owner: the performance marketer. Type: master sheet (edit in place,
soft delete). Created when a campaign is planned — a handful per month, not daily.

| Col | Header | Type | Req | Notes |
|---|---|---|---|---|
| A | `campaign_id` | Text | yes | PK `CMP-YYYY-NNN`, e.g. `CMP-2026-001`. Immutable. |
| B | `campaign_name` | Text | yes | Human name, e.g. "Monsoon Asthma Awareness" |
| C | `utm_campaign` | Text | yes | The join key used in URLs + ad platforms + creatives. lowercase-hyphenated, e.g. `monsoon-asthma-2026`. Unique. |
| D | `objective` | Enum | yes | `AWARENESS` / `TRAFFIC` / `CONVERSIONS` / `RETENTION` |
| E | `channels` | Text | yes | Channels this campaign runs on, pipe-separated enum values, e.g. `META\|GOOGLE\|INFLUENCER` |
| F | `focus_sku` | Text (FK → catalog/inventory) | no | Primary product pushed, e.g. `AQM-PRO-01` |
| G | `start_date` | Date | yes | `YYYY-MM-DD` |
| H | `end_date` | Date | conditional | Blank if always-on |
| I | `status` | Enum | yes | `PLANNED` / `ACTIVE` / `PAUSED` / `COMPLETED` |
| J | `total_budget` | Number (INR) | yes | Planned spend across all channels |
| K | `owner_id` | Text (FK → hr-employee-master) | yes | Who runs it |
| L | `target_metric` | Enum | yes | `ROAS` / `CAC` / `REVENUE` / `CONVERSIONS` / `REACH` / `CTR` |
| M | `target_value` | Number | yes | The goal for `target_metric` |
| N | `notes` | Text | no | |

What's NOT stored: actual spend/revenue/ROAS (rolled up from the performance layers), days running.

---

## 2. `mkt-ad-performance` (paid — daily transaction)

One row per **campaign × platform × day**. Append-only; this is the raw daily export from Meta/Google
Ads. Owner: performance marketer.

| Col | Header | Type | Req | Notes |
|---|---|---|---|---|
| A | `perf_id` | Text | yes | PK `ADP-YYYY-NNNNN`. Immutable. |
| B | `date` | Date | yes | The performance day, `YYYY-MM-DD` |
| C | `campaign_id` | Text (FK → mkt-campaigns) | yes | |
| D | `utm_campaign` | Text | yes | Denormalized join key (also reconciles to sales orders) |
| E | `platform` | Enum | yes | `META` / `GOOGLE` (extend as needed) |
| F | `ad_set` | Text | no | Optional ad-set/ad-group name for finer reads |
| G | `spend` | Number (INR) | yes | Spend that day |
| H | `impressions` | Number | yes | |
| I | `clicks` | Number | yes | |
| J | `conversions` | Number | yes | Platform-reported conversions |
| K | `conversion_value` | Number (INR) | yes | Platform-reported revenue (0 if none) |
| L | `notes` | Text | no | |

What's NOT stored (computed): CTR = clicks/impressions, CPC = spend/clicks, CPM = spend/impressions×1000,
CAC = spend/conversions, ROAS = conversion_value/spend, plus all weekly/monthly/campaign rollups.

Natural key: `(date, campaign_id, platform, ad_set)`.

---

## 3. `mkt-influencer-collabs` (influencer — one row per collab)

One row per influencer collaboration/post. Append-only. A collab is an *event*, not a daily series — so
it lives in its own sheet rather than being forced into the daily paid grain.

| Col | Header | Type | Req | Notes |
|---|---|---|---|---|
| A | `collab_id` | Text | yes | PK `INF-YYYY-NNN`. Immutable. |
| B | `campaign_id` | Text (FK → mkt-campaigns) | yes | |
| C | `utm_campaign` | Text | yes | Join key |
| D | `influencer_name` | Text | yes | |
| E | `handle` | Text | yes | @handle |
| F | `platform` | Enum | yes | `INSTAGRAM` / `YOUTUBE` / `OTHER` |
| G | `deliverable` | Enum | yes | `REEL` / `POST` / `STORY` / `VIDEO` / `BUNDLE` |
| H | `go_live_date` | Date | yes | |
| I | `fee` | Number (INR) | yes | Flat fee paid |
| J | `promo_code` | Text | no | Discount code = attribution key into sales orders |
| K | `reach` | Number | no | Reported reach/views |
| L | `engagement` | Number | no | Likes + comments + saves |
| M | `orders_attributed` | Number | no | Orders via promo_code (from sales, filled later) |
| N | `status` | Enum | yes | `NEGOTIATING` / `BOOKED` / `LIVE` / `COMPLETED` / `CANCELLED` |
| O | `notes` | Text | no | |

What's NOT stored (computed): cost-per-order = fee/orders_attributed, engagement rate = engagement/reach.

---

## 4. `creatives-index.csv` (asset library index)

One row per creative file. This is what lets the downstream agent connect an asset to its results.

| Col | Header | Type | Req | Notes |
|---|---|---|---|---|
| A | `creative_id` | Text | yes | PK `CRV-YYYY-NNNN`. Immutable. |
| B | `campaign_id` | Text (FK → mkt-campaigns) | yes | |
| C | `utm_campaign` | Text | yes | Join key |
| D | `file_path` | Text | yes | Relative path under `creatives/` (see naming convention) |
| E | `format` | Enum | yes | `STATIC` / `VIDEO` / `CAROUSEL` / `STORY` |
| F | `platform` | Enum | yes | `META` / `GOOGLE` / `INSTAGRAM` / `YOUTUBE` |
| G | `headline` | Text | no | Primary copy/hook on the creative |
| H | `concept` | Text | no | Short label for the creative angle, e.g. "kids-health-fear", "clean-air-aspirational" |
| I | `variant` | Text | no | A/B variant tag, e.g. `A`, `B` |
| J | `created_date` | Date | yes | |
| K | `status` | Enum | yes | `DRAFT` / `LIVE` / `PAUSED` / `WINNER` / `RETIRED` |
| L | `notes` | Text | no | |

What's NOT stored (computed): performance per creative — the downstream agent joins this to ad performance
via `utm_campaign` + ad-set/creative naming to learn which `concept`/`variant` wins.

---

## Join integrity (verify after seeding)

- Every `utm_campaign` in ad-performance, influencer-collabs, and creatives-index must exist in
  `mkt-campaigns`.
- Every `campaign_id` likewise.
- IDs unique within each file; enums within the allowed sets; dates ISO; CSVs parse.
- The same `utm_campaign` is the bridge to `sales-d2c-orders` (its `coupon_code`/UTM) for true revenue —
  keep codes consistent with how sales records them.
