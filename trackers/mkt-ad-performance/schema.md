# `mkt-ad-performance` — schema

The raw paid feed. **One row per campaign × platform × day** — the daily export from Meta / Google / Amazon Ads. Append-only. This is the layer all paid rollups (CTR, CPC, CPM, CAC, ROAS, weekly/monthly totals) are computed from.

**Category**: Marketing (`mkt-*`, header color Pink `#EC4899`)
**Tier**: T2
**Type**: Transaction sheet (append-only)
**Owner**: Performance Marketer (`EMP-017`, Sandeep Bhat)
**Daily effort**: ~5 minutes — paste each platform's day numbers.

## Grain: one row per campaign × platform × day

Don't pre-aggregate. One campaign running on Meta and Google on the same day is two rows. Weekly/monthly views are computed, never stored.

## Tab structure

v1: one tab, `data`.

## Columns (12)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `perf_id` | Text | yes | PK `ADP-YYYY-NNNNN`, e.g. `ADP-2026-00001`. Immutable. Monospace. |
| B | `date` | Date | yes | The performance day, `YYYY-MM-DD` |
| C | `campaign_id` | Text (FK → `mkt-campaigns`) | yes | |
| D | `utm_campaign` | Text | yes | Denormalized join key (also reconciles to `sales-d2c-orders`) |
| E | `platform` | Enum | yes | `META` / `GOOGLE` / `AMAZON` |
| F | `ad_set` | Text | no | Ad-set / ad-group name; match to creative `concept-v<variant>` to close the loop |
| G | `spend` | Number (INR) | yes | Spend that day (`₹ #,##,##0`) |
| H | `impressions` | Number | yes | |
| I | `clicks` | Number | yes | |
| J | `conversions` | Number | yes | Platform-reported conversions |
| K | `conversion_value` | Number (INR) | yes | Platform-reported revenue (0 if none) |
| L | `notes` | Text | no | |

## Enums

### `platform` (E)
`META` · `GOOGLE` · `AMAZON`

_(Extended from the base spec to include `AMAZON` since the account runs Amazon Ads. Extend further as needed.)_

## Validation rules to set
1. Column A (`perf_id`): protected; unique.
2. Column B (`date`): Date validation.
3. Column E (`platform`): Dropdown.
4. Columns G–K: Number ≥ 0; `spend`/`conversion_value` currency-formatted.
5. On read, flag a row where `clicks > impressions` or `conversions` has revenue but `conversion_value = 0`.

## What's NOT stored (Claude computes on the fly)
- **CTR** = clicks / impressions
- **CPC** = spend / clicks
- **CPM** = spend / impressions × 1000
- **CAC** = spend / conversions
- **ROAS** = conversion_value / spend
- **Conversion rate** = conversions / clicks
- All **weekly / monthly / per-campaign / per-channel** rollups.

## Natural key
`(date, campaign_id, platform, ad_set)`.

## Relationships
| Tracker | References via | Cardinality |
|---|---|---|
| `mkt-campaigns` | `campaign_id` + `utm_campaign` | many → 1 |
| `creatives-index` | `utm_campaign` (+ `ad_set` ↔ `concept`/`variant`) | join for creative learnings |
| `sales-d2c-orders` | `utm_campaign` ↔ `coupon_code` / UTM | join for true revenue |
