# Design Bible — condensed (house rules every tracker follows)

These are the conventions the existing Company OS trackers use. Match them so the marketing trackers feel
native. (If the full `docs/04-tracker-design-bible.md` exists in the repo, defer to it.)

## Schema discipline
- **Stable IDs.** Every row has an immutable, prefixed ID: `CMP-2026-001`, `ADP-2026-00042`. Prefix names
  the table. Never reuse or renumber.
- **Soft delete.** Never delete rows; use `is_active` (TRUE/FALSE) or a `status` enum. Preserves history.
- **ISO dates.** All dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` IST. Lexicographic = chronological.
- **Enums, not free text.** Fixed value sets use SCREAMING_SNAKE_CASE and a dropdown. `ACTIVE`, not "active".
- **One concept per sheet.** A sheet is one entity; relationships use `*_id` foreign keys. Don't duplicate
  names/descriptions across sheets — reference by ID and denormalize only a readable label where handy.
- **Master vs transaction.** Masters change rarely, edited in place (campaigns). Transactions are
  append-only, one row per event (daily ad performance). Keep them separate.

## Naming
- Sheet/tracker names: `[category]-[noun]`, lowercase-hyphen → `mkt-campaigns`, `mkt-ad-performance`.
- Columns: `snake_case`. Foreign keys `<entity>_id`. Booleans `is_*`/`has_*`. Dates `*_date`. Timestamps `*_at`.

## Compute, don't store
Derived values (ROAS, CAC, CTR, weekly totals) are computed by Claude on read, not stored in cells. Each
schema.md ends with a "What's NOT stored (computed on the fly)" section listing them. The sheet is the
source; the agent is the lens.

## Visual system
- Category color = header background, white bold text. **Marketing (`mkt-*`) = Pink `#EC4899`.**
- Status-pill conditional formatting: green for good/active, amber for pending, red for fail/critical,
  gray for archived.
- Freeze header + ID column; zebra striping; monospace IDs; right-aligned tabular numbers; `₹` with Indian
  grouping for currency.

## The standard tracker folder
Each tracker is a folder: `schema.md` (column-by-column spec applying these rules) + `sample-data.csv`
(8–20 realistic seed rows). Optionally `visual-spec.md`, `claude-tips.md`. Keep schema.md focused and
include: purpose line, category/tier/type/owner, tab structure, the column table, enums, validation rules,
the "NOT stored" section, natural key, and relationships.
