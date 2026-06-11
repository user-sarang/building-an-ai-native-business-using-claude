# `mkt-campaigns` — schema

The planning spine for all marketing. **One row per campaign initiative** — a channel-agnostic push that spans weeks. This is the master that the daily paid rows (`mkt-ad-performance`) and per-collab influencer rows (`mkt-influencer-collabs`) hang off, joined by `campaign_id` + `utm_campaign`.

**Category**: Marketing (`mkt-*`, header color Pink `#EC4899`)
**Tier**: T2
**Type**: Master sheet (edit in place, soft delete via `status`)
**Owner**: Performance Marketer (`EMP-017`, Sandeep Bhat)
**Created when**: a campaign is planned — a handful per month, not daily.

## Grain: one row per campaign

A campaign is created once and lives for its whole run. The performance *data* underneath arrives at channel-native cadence (daily for paid, per-post for influencer) in the other two trackers. Never store daily numbers here.

## Tab structure

v1: one tab, `data`.

## Columns (14)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `campaign_id` | Text | yes | PK `CMP-YYYY-NNN`, e.g. `CMP-2026-001`. Immutable. Monospace. |
| B | `campaign_name` | Text | yes | Human name, e.g. "Always-On Conversions" |
| C | `utm_campaign` | Text | yes | The join key in URLs + ad platforms + creatives + sales coupon/UTM. lowercase-hyphenated. **Unique.** |
| D | `objective` | Enum | yes | `AWARENESS` / `TRAFFIC` / `CONVERSIONS` / `RETENTION` |
| E | `channels` | Text | yes | Pipe-separated channel enums, e.g. `META\|GOOGLE` |
| F | `focus_sku` | Text (FK → `inv-finished-goods`) | no | Primary product pushed, e.g. `AQM-PRO-01` |
| G | `start_date` | Date | yes | `YYYY-MM-DD` |
| H | `end_date` | Date | conditional | Blank if always-on |
| I | `status` | Enum | yes | `PLANNED` / `ACTIVE` / `PAUSED` / `COMPLETED` |
| J | `total_budget` | Number (INR) | yes | Planned spend across all channels (`₹ #,##,##0`) |
| K | `owner_id` | Text (FK → `hr-employee-master`) | yes | Who runs it |
| L | `target_metric` | Enum | yes | `ROAS` / `CAC` / `REVENUE` / `CONVERSIONS` / `REACH` / `CTR` |
| M | `target_value` | Number | yes | The goal for `target_metric` |
| N | `notes` | Text | no | |

## Enums

### `objective` (D)
`AWARENESS` · `TRAFFIC` · `CONVERSIONS` · `RETENTION`

### `channels` (E) — pipe-separated values from
`META` · `GOOGLE` · `AMAZON` · `INFLUENCER` · `EMAIL` · `ORGANIC`

### `status` (I)
`PLANNED` · `ACTIVE` · `PAUSED` · `COMPLETED`

### `target_metric` (L)
`ROAS` · `CAC` · `REVENUE` · `CONVERSIONS` · `REACH` · `CTR`

## Validation rules to set
1. Column A (`campaign_id`): protected; unique.
2. Column C (`utm_campaign`): unique; lowercase-hyphenated.
3. Columns D, I, L (enums): Data Validation → Dropdown.
4. Columns G, H: Date validation; `end_date` ≥ `start_date` when present.
5. Column J (`total_budget`): Number ≥ 0; currency-formatted `₹ #,##,##0`.

## What's NOT stored (Claude computes on the fly)
- **Actual spend / revenue / ROAS / CAC** — rolled up from `mkt-ad-performance` and `mkt-influencer-collabs` via `utm_campaign`.
- **Days running / pacing** — derived from `start_date` and today.
- **Target vs actual** — compared at report time.

## Natural key
`campaign_id` (PK); `utm_campaign` is a unique alternate key.

## Relationships
| Tracker | References via | Cardinality |
|---|---|---|
| `mkt-ad-performance` | `campaign_id` + `utm_campaign` | 1 → many |
| `mkt-influencer-collabs` | `campaign_id` + `utm_campaign` | 1 → many |
| `creatives-index` | `campaign_id` + `utm_campaign` | 1 → many |
| `inv-finished-goods` | `focus_sku` | many → 1 |
| `hr-employee-master` | `owner_id` | many → 1 |
| `sales-d2c-orders` | `utm_campaign` ↔ `coupon_code` / UTM | for true revenue |
