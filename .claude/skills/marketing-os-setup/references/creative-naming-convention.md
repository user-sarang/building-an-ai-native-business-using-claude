# Creative storage & naming convention

The point of this convention is **traceability**: a downstream agent (or a human) should be able to look
at any creative file and know which campaign it served, what concept it tested, and — by joining to ad
performance — whether it won. Storage is dumb; the `creatives-index.csv` is the brain.

## Folder layout

```
creatives/
  README.md                     <- this convention, written for the next agent
  creatives-index.csv           <- one row per asset (schema in tracker-schemas.md §4)
  <utm_campaign>/               <- one folder per campaign, named by its utm_campaign
    <files…>
```

Group by `utm_campaign` (not by date or platform) because that's the unit the agent reasons about.

## File naming

```
<utm_campaign>__<platform>__<format>__<concept>__v<variant>.<ext>
```

- `utm_campaign` — matches the campaign exactly (e.g. `monsoon-asthma-2026`)
- `platform` — `meta` / `google` / `instagram` / `youtube`
- `format` — `static` / `video` / `carousel` / `story`
- `concept` — short kebab label for the angle (`kids-health-fear`, `clean-air-aspirational`, `price-offer`)
- `variant` — `a`, `b`, `c`… for A/B tests of the same concept
- double-underscore `__` separates fields so they parse cleanly even if a field contains a single hyphen

**Example:** `monsoon-asthma-2026__meta__video__kids-health-fear__va.mp4`

## Rules

1. **Every asset gets a row in `creatives-index.csv`** at creation, with a `creative_id`, its `campaign_id`,
   `utm_campaign`, `file_path`, `format`, `platform`, `concept`, `variant`, and `status=DRAFT`.
2. **The filename and the index row must agree** on utm_campaign/platform/format/concept/variant. The index
   is authoritative; the filename is the human-readable mirror.
3. **Status lifecycle:** `DRAFT → LIVE → (WINNER | PAUSED) → RETIRED`. Mark a clear winner `WINNER` so the
   downstream agent can prioritize lookalikes of it.
4. **Match `concept`/`variant` to the ad-set naming** in `mkt-ad-performance` where possible, so performance
   can be attributed back to the exact creative angle. If the ad platform's ad-set is named
   `<concept>-v<variant>`, the loop closes automatically.
5. **Never rename a shipped file.** If a creative changes materially, it's a new variant with a new row.

## How the downstream agent learns "what works"

Join `creatives-index.csv` → `mkt-ad-performance` on `utm_campaign` (+ ad-set/concept), aggregate spend,
conversions and ROAS per `concept`/`variant`, and rank. The winning concepts inform the next round of
creative briefs. That's the whole feedback loop this convention is built to enable.
