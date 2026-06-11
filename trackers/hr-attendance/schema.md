# `hr-attendance` — schema

Daily attendance record. One row per employee per day. **Fully manual** — no formulas, no scripts, no auto-anything. Data Validation dropdowns are the only "smart" element, and those are just constraint rules.

**Category**: HR
**Tier**: T1 (foundational, week 1)
**Type**: Transaction sheet (append-only)
**Owner**: HR-admin (one person)
**Daily effort**: ~5 minutes

## Tab structure

**One tab only**: `data`.

No dashboard tab, no config tab. Charts and pivots can be added later as needed; for v1 we keep it dead simple.

## Columns

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `date` | Date | yes | Format `YYYY-MM-DD` |
| B | `employee_id` | Text | yes | Stable employee ID, e.g. `EMP-007` |
| C | `employee_name` | Text | yes | Full name, typed (no lookup) |
| D | `status` | Enum (dropdown) | yes | See enum below |
| E | `check_in` | Time | conditional | `HH:MM` (24h) — required if status ∈ {PRESENT, HALF_DAY, WFH, FIELD-equivalent} |
| F | `check_out` | Time | conditional | `HH:MM` (24h) — required if check_in is set |
| G | `location` | Enum (dropdown) | yes | See enum below |
| H | `notes` | Text | no | Free text — reason for late / absence / context |

## Enums

### `status` (column D)

| Value | Meaning |
|---|---|
| `PRESENT` | Full day worked |
| `WFH` | Work from home |
| `HALF_DAY` | Partial day |
| `LEAVE` | Approved leave (uses leave balance) |
| `ABSENT` | No-show, no leave applied |
| `HOLIDAY` | Public holiday or weekly off |

### `location` (column G)

| Value | Meaning |
|---|---|
| `OFFICE` | Bengaluru main office |
| `FACTORY` | Manufacturing floor |
| `WFH` | Working from home |
| `FIELD` | Site visit, customer location, etc. |
| `LEAVE` | Not working today |

Dropdowns are configured via **Data → Data Validation** on columns D and G. The values are hardcoded directly in the validation rule (no config tab needed).

## Audit / change history

We rely on **Google Sheets' built-in version history** (File → Version History → See version history) for audit. No `created_at` / `created_by` columns.

## What's NOT stored (Claude computes on the fly)

- **Hours worked** — Claude computes from `check_out - check_in` when asked.
- **Late minutes** — Claude computes from `check_in - 09:30` when asked.
- **Attendance percentage** — Claude computes from filtered counts when asked.

This keeps the sheet uncluttered. The data is the source; Claude is the lens.

## Natural key

`(date, employee_id)` is the unique identifier for a row. No separate ID column.

## Validation rules to set

1. Column A (`date`): Data Validation → Date → Is valid date
2. Column D (`status`): Data Validation → Dropdown (chip style) → 6 values listed above
3. Column G (`location`): Data Validation → Dropdown (chip style) → 5 values listed above
4. Columns E, F (`check_in`, `check_out`): Format → Number → Time → `HH:mm`

## Growth & archival

- ~20 rows/day × ~22 working days/month = ~440 rows/month
- ~5,200 rows/year
- Sheets handles this comfortably. No splitting needed.
- Archive policy: after 2 fiscal years, create a copy as `hr-attendance-archive-YYYY` and clear from active sheet.
