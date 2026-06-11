# HANDOFF — Marketing OS for abc

For the downstream **marketing-head** agent. Everything you need to run daily/weekly/monthly reports and bid/budget adjustments is below.

## The business in one line
abc sells an on-desk AQI + clock monitor (catalog SKU `AQM-PRO-01`, "AirSense Pro", ₹4,999), B2C, India, marketplace-led today. Differentiator: display quality + battery life. Voice: clear, no-nonsense, no emojis, plain numbers. Full detail in `brand-profile.md`.

## Where everything lives
```
trackers/mkt-campaigns/          schema.md + sample-data.csv   (planning spine — 1 row/campaign)
trackers/mkt-ad-performance/     schema.md + sample-data.csv   (paid — 1 row/campaign/platform/day)
trackers/mkt-influencer-collabs/ schema.md + sample-data.csv   (influencer — pilot; a few collabs live)
marketing/
  brand-profile.md               brand, voice, audience, KPIs
  reporting-spec.md               what each report must show
  creatives/README.md             creative naming + index rules
  creatives/creatives-index.csv   1 row per asset → campaign → concept/variant
  creatives/<utm_campaign>/        the asset files
reports/marketing/{daily,weekly,monthly}/  generated reports land here (unified outputs root)
```

## The join key (most important thing)
**`utm_campaign`** is the bridge across every layer:
- `mkt-campaigns.utm_campaign` (master, unique) →
- `mkt-ad-performance.utm_campaign` (daily paid) and `mkt-influencer-collabs.utm_campaign` (per collab) and `creatives-index.utm_campaign` (assets).
- For **true revenue**, reconcile `utm_campaign` to `sales-d2c-orders` via its `coupon_code` / UTM. Platform-reported `conversion_value` in `mkt-ad-performance` is the fast signal; sales orders are the truth — prefer sales when both exist.

`campaign_id` (`CMP-YYYY-NNN`) is the secondary join. Creative `concept`/`variant` (e.g. `battery-life` / `A`) matches the `ad_set` naming in `mkt-ad-performance` (e.g. `battery-life-a`) so you can attribute ROAS to a specific creative angle.

## Nothing is pre-computed
ROAS, CAC, CTR, CPC, CPM, conversion rate, and all weekly/monthly/per-channel totals are **computed by you on read** from the daily rows. Don't expect stored totals.

## Current state (seeded)
- 4 campaigns: 3 ACTIVE always-on (`always-on-conversions-2026` Meta+Google, `desk-upgrade-awareness-2026` Meta, `amazon-sponsored-2026` Amazon) + 1 PLANNED seasonal (`pollution-season-2026`).
- 16 days of sample paid rows across 2026-06-06 → 2026-06-09.
- 3 creatives indexed (battery-life A/B, desk-aesthetic A).
- Influencer: planned, no rows yet.
- Owners: Sandeep Bhat (`EMP-017`, paid), Pooja Desai (`EMP-016`, influencer/organic).

## Targets to report against
ROAS 3.0× · CAC ≤ ₹1,500 (confirm) · CTR ≥ 1.5% · conversion-rate baseline TBD. Cadence: daily pacing + weekly review + monthly board number. See `reporting-spec.md`.

## Open items to confirm with the founder
- Seasonality (pollution-season assumption is a placeholder).
- Real competitor head-to-heads, secondary brand color, logo rules, ad account handles, website URL.
- CAC target and a conversion-rate baseline once a few weeks of data exist.
