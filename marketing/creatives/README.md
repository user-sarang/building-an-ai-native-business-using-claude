# Creatives — storage & naming convention

The point of this folder is **traceability**: any agent (or human) should be able to look at a creative file and know which campaign it served, what concept it tested, and — by joining to `mkt-ad-performance` — whether it won. Storage is dumb; `creatives-index.csv` is the brain.

## Folder layout
```
creatives/
  README.md                     <- this file
  creatives-index.csv           <- one row per asset (schema in mkt-* tracker-schemas §4)
  <utm_campaign>/               <- one folder per campaign, named by its utm_campaign
    <files…>
```
Group by `utm_campaign` (not date or platform) — that's the unit we reason about.

## File naming
```
<utm_campaign>__<platform>__<format>__<concept>__v<variant>.<ext>
```
- `utm_campaign` — matches the campaign exactly (e.g. `always-on-conversions-2026`)
- `platform` — `meta` / `google` / `amazon` / `instagram` / `youtube`
- `format` — `static` / `video` / `carousel` / `story`
- `concept` — short kebab label for the angle (`battery-life`, `desk-aesthetic`, `display-clarity`, `price-offer`)
- `variant` — `a`, `b`, `c`… for A/B tests of the same concept
- double-underscore `__` separates fields so they parse cleanly even with a single hyphen inside a field

**Example:** `always-on-conversions-2026__meta__video__battery-life__vb.mp4`

## Rules
1. **Every asset gets a row in `creatives-index.csv`** at creation: `creative_id`, `campaign_id`, `utm_campaign`, `file_path`, `format`, `platform`, `concept`, `variant`, `status=DRAFT`.
2. **Filename and index row must agree** on utm_campaign/platform/format/concept/variant. The index is authoritative; the filename mirrors it.
3. **Status lifecycle:** `DRAFT → LIVE → (WINNER | PAUSED) → RETIRED`. Mark clear winners `WINNER` so the next round can make lookalikes.
4. **Match `concept`/`variant` to the `ad_set` naming** in `mkt-ad-performance` (e.g. ad-set `battery-life-a`) so performance attributes back to the exact angle — the loop closes automatically.
5. **Never rename a shipped file.** A material change is a new variant with a new row.

## How "what works" gets learned
Join `creatives-index.csv` → `mkt-ad-performance` on `utm_campaign` (+ ad-set/concept), aggregate spend, conversions and ROAS per `concept`/`variant`, and rank. Winning concepts feed the next creative brief. That's the whole feedback loop.

## abc's formats in play
Static images, video / reels, carousels, and clean product photos (marketplace style). Lead concepts so far: `battery-life`, `desk-aesthetic`, `display-clarity`.
