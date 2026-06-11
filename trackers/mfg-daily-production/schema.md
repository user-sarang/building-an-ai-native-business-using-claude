# `mfg-daily-production` — schema

The daily heartbeat of the factory floor. One row per **station, per shift, per product, per day** — so you can see exactly where units were built, where they were lost, and where the line stalled. This is the tracker that answers "did we make our ~45/day to hit 1000 this month?"

**Category**: Manufacturing (`mfg-*`, header color Orange `#F97316`)
**Tier**: T1 (foundational, week 1)
**Type**: Transaction sheet (append-only)
**Owner**: Production Lead (`EMP-005`, Vikram)
**Daily effort**: ~5 minutes at end of each shift
**Scope**: Manufactured goods only (AQI monitors). White-label speakers are *purchased*, not produced — they appear in `inv-finished-goods`, never here.

## Tab structure

**One tab only**: `data`.

No dashboard or config tab for v1 — same philosophy as `hr-attendance`. KPIs (daily total, yield %, achievement %) are computed by Claude on the fly, not stored. Dropdowns are the only "smart" element.

## Columns (14)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `production_id` | Text | yes | Primary key. Format `MDP-YYYY-NNNN`, e.g. `MDP-2026-0001`. Immutable. Monospace. |
| B | `date` | Date | yes | Format `YYYY-MM-DD` |
| C | `shift` | Enum (dropdown) | yes | See enum below |
| D | `station` | Enum (dropdown) | yes | The build step. See enum below |
| E | `product_sku` | Text (FK → `cat-sku-master`) | yes | SKU code, e.g. `AQM-PRO-01`. Manufactured AQI monitors only. |
| F | `product_name` | Text | yes | Denormalized readable name (typed, no lookup) — mirrors `employee_name` in attendance |
| G | `operator_id` | Text (FK → `hr-employee-master`) | yes | `employee_id` running the station, e.g. `EMP-006` |
| H | `operator_name` | Text | yes | Denormalized preferred name |
| I | `target_qty` | Number | yes | Planned units for this station/shift (from `mfg-production-plan`, future) |
| J | `units_completed` | Number | yes | **Good** units that passed this station |
| K | `units_rejected` | Number | yes | Units scrapped/failed at this station (≥ 0; 0 if none) |
| L | `rework_qty` | Number | no | Units pulled for rework (not scrapped, not yet passed) |
| M | `downtime_minutes` | Number | no | Minutes the station was stopped this shift (0 or blank if none) |
| N | `notes` | Text | no | Free text — defect reason, material shortage, machine issue, context |

## Enums

### `shift` (column C)

| Value | Meaning |
|---|---|
| `GENERAL` | Single general shift (9:30–18:30) — the default at current volume |
| `SHIFT_A` | Morning shift (used only when running two shifts for a rush) |
| `SHIFT_B` | Afternoon/evening shift |

### `station` (column D) — the AQI monitor build line, in flow order

| Value | Meaning |
|---|---|
| `SUB_ASSEMBLY` | PCB + sensor module mounted into chassis, wiring |
| `CALIBRATION` | PM2.5 / gas sensor calibrated against reference unit — the critical step for an AQI product |
| `FINAL_ASSEMBLY` | Enclosure closed, display fitted, firmware flashed |
| `TESTING` | Functional + burn-in test, QC sign-off |
| `PACKING` | Boxed, serial registered, labeled, moved to finished-goods |

> A unit flows **SUB_ASSEMBLY → CALIBRATION → FINAL_ASSEMBLY → TESTING → PACKING**. `units_completed` at `PACKING` is what increments finished-goods stock.

## Validation rules to set

1. Column A (`production_id`): protected; only the Production Lead edits. Unique.
2. Column B (`date`): Data Validation → Date → Is valid date.
3. Column C (`shift`): Data Validation → Dropdown (chip style) → 3 values above.
4. Column D (`station`): Data Validation → Dropdown (chip style) → 5 values above.
5. Columns I, J, K, L, M (quantities): Data Validation → Number → ≥ 0.
6. `units_completed + units_rejected + rework_qty` should not exceed what entered the station (sanity-check on read, not enforced).

## What's NOT stored (Claude computes on the fly)

- **Daily output** — sum of `units_completed` at `PACKING` for a date.
- **First-pass yield** — `units_completed / (units_completed + units_rejected)` per station.
- **Plan achievement %** — `units_completed / target_qty`.
- **Monthly run-rate vs 1000-unit goal** — cumulative packed units / working days elapsed.
- **Bottleneck station** — the station with lowest throughput or highest downtime.
- **Scrap cost** — `units_rejected × unit_cost` (joins to `inv-finished-goods` / `cat-sku-master`).

Same principle as the rest of the OS: the sheet is the source, Claude is the lens.

## Natural key

`(date, shift, station, product_sku)` is unique. The `production_id` is the stable surrogate key used by any future joins.

## Audit / change history

Like `hr-attendance`, we rely on **Google Sheets' built-in version history** (File → Version History) rather than `created_at` / `created_by` columns. Keeps end-of-shift entry to a few seconds. (If this tracker later feeds payroll incentives or scrap-cost accounting, add the four audit columns from the Design Bible §A.4.)

## Relationships

| Tracker | References via | Cardinality |
|---|---|---|
| `hr-employee-master` | `operator_id` → `employee_id` | many → 1 |
| `cat-sku-master` (future) | `product_sku` → `sku_id` | many → 1 |
| `inv-finished-goods` | `PACKING` completions increment `qty_on_hand` | feeds |
| `qc-final` (future) | per-unit pass/fail detail behind `units_rejected` | 1 → many |

## Growth & archival

- ~5 stations × 1 shift × ~22 working days = ~110 rows/month, ~1,300/year.
- Sheets handles this for years. Archive policy: after 2 fiscal years, copy to `mfg-daily-production-archive-YYYY` and clear from active.
