# `mkt-influencer-collabs` — schema

**One row per influencer collaboration / post.** A collab is an *event*, not a daily series, so it lives in its own sheet rather than being forced into the daily paid grain. Append-only.

> **Status:** Influencer is in **pilot** for abc (first collabs went live May 2026). Add a row per collab and tie it to a campaign via `utm_campaign`; fill `orders_attributed` from `sales-d2c-orders` using the `promo_code`.

**Category**: Marketing (`mkt-*`, header color Pink `#EC4899`)
**Tier**: T2
**Type**: Transaction sheet (append-only)
**Owner**: Content & Social Lead (`EMP-016`, Pooja Desai)

## Grain: one row per collab/post

## Tab structure
v1: one tab, `data`.

## Columns (15)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `collab_id` | Text | yes | PK `INF-YYYY-NNN`, e.g. `INF-2026-001`. Immutable. Monospace. |
| B | `campaign_id` | Text (FK → `mkt-campaigns`) | yes | |
| C | `utm_campaign` | Text | yes | Join key |
| D | `influencer_name` | Text | yes | |
| E | `handle` | Text | yes | @handle |
| F | `platform` | Enum | yes | `INSTAGRAM` / `YOUTUBE` / `OTHER` |
| G | `deliverable` | Enum | yes | `REEL` / `POST` / `STORY` / `VIDEO` / `BUNDLE` |
| H | `go_live_date` | Date | yes | `YYYY-MM-DD` |
| I | `fee` | Number (INR) | yes | Flat fee paid (`₹ #,##,##0`) |
| J | `promo_code` | Text | no | Discount code = attribution key into `sales-d2c-orders` |
| K | `reach` | Number | no | Reported reach / views |
| L | `engagement` | Number | no | Likes + comments + saves |
| M | `orders_attributed` | Number | no | Orders via `promo_code` (filled from sales later) |
| N | `status` | Enum | yes | `NEGOTIATING` / `BOOKED` / `LIVE` / `COMPLETED` / `CANCELLED` |
| O | `notes` | Text | no | |

## Enums
### `platform` (F)
`INSTAGRAM` · `YOUTUBE` · `OTHER`
### `deliverable` (G)
`REEL` · `POST` · `STORY` · `VIDEO` · `BUNDLE`
### `status` (N)
`NEGOTIATING` · `BOOKED` · `LIVE` · `COMPLETED` · `CANCELLED`

## Validation rules to set
1. Column A (`collab_id`): protected; unique.
2. Columns F, G, N (enums): Dropdown.
3. Column H (`go_live_date`): Date validation.
4. Columns I, K, L, M: Number ≥ 0; `fee` currency-formatted.

## What's NOT stored (Claude computes on the fly)
- **Cost per order** = fee / orders_attributed
- **Engagement rate** = engagement / reach
- Per-campaign and monthly influencer rollups.

## Natural key
`collab_id` (PK). `(handle, go_live_date)` is unique in practice.

## Relationships
| Tracker | References via | Cardinality |
|---|---|---|
| `mkt-campaigns` | `campaign_id` + `utm_campaign` | many → 1 |
| `sales-d2c-orders` | `promo_code` ↔ `coupon_code` | join for attributed orders |
