# Tracker Design Bible

The rules every tracker in this Company OS follows. Two purposes:

1. Makes the data **trustworthy** — Claude Code can rely on consistent schemas, types, and naming.
2. Makes the trackers **visually beautiful** — so participants of the bootcamp say "I want sheets that look like *that*."

This document is the foundational lesson of the bootcamp. Every other tracker in the repo is a worked example of these rules.

---

## A. Schema discipline

Every sheet, every time.

### A.1 — Stable IDs
- Every row has an `id` column.
- IDs are immutable. Never reuse, never re-number on delete.
- Prefer short prefixed IDs: `EMP-001`, `PO-2026-0142`, `TKT-00873`. Prefix tells you the table at a glance.

### A.2 — Soft delete only
- Never delete rows. Add an `is_active` column (TRUE/FALSE) or a `status` enum.
- Preserves history. Makes audits possible. Lets Claude Code answer "who left the company?"

### A.3 — Date and time format
- All dates: `YYYY-MM-DD` (ISO 8601). Never `DD/MM/YYYY`.
- All timestamps: `YYYY-MM-DD HH:MM:SS` in IST (UTC+5:30). Store TZ if ambiguous.
- Reason: lexicographic sort = chronological sort. Claude can compare strings without parsing.

### A.4 — Audit columns
Every transaction sheet has:
- `created_at` — timestamp
- `created_by` — employee_id of who created the row
- `updated_at` — last edit timestamp
- `updated_by` — last editor

### A.5 — Enums, not free text
For any status, category, or type column:
- Define the allowed values up front.
- Enforce via Data Validation (dropdown).
- Use SCREAMING_SNAKE_CASE: `OPEN`, `IN_PROGRESS`, `DONE`, `BLOCKED`.
- Never `open` vs `Open` vs `opn`.

### A.6 — One concept per sheet
- Employee master is NOT attendance is NOT payroll.
- A sheet contains one *entity*. Relationships use foreign-key IDs.
- A sheet may have multiple **tabs**: `data`, `dashboard`, `config`, `archive`. But all tabs serve one concept.

### A.7 — Master vs transaction
| Master sheet | Transaction sheet |
|---|---|
| Changes rarely | Append-only |
| ~10s–100s of rows | 100s–1000s+ |
| Examples: Employee, Vendor, SKU, Customer | Examples: Attendance, PO, Ticket, Order |
| Edits in-place | New row per event |

Transactions reference masters via `*_id` columns. Never duplicate names or descriptions.

---

## B. Validation as guardrails

### B.1 — Dropdowns everywhere
Any column with a fixed set of values uses Data Validation → Dropdown.

### B.2 — Number ranges
Quantities, scores, percentages: set min/max via validation.

### B.3 — Date pickers
Date columns use the Date data validation type. Forces correct format.

### B.4 — Required columns
Mark required columns visually (header in red asterisk or italics) and via validation rejecting blanks.

### B.5 — Protected ranges
- ID columns: protect, only the owner can edit.
- Computed columns (formulas): protect entirely.
- Master sheets: editor list restricted.

---

## C. Naming conventions

### C.1 — Sheet names
`[category]-[noun]`, lowercase, hyphens.
Examples: `hr-attendance`, `fin-cashflow`, `mfg-daily-production`.

### C.2 — Tab names
Inside each sheet:
- `data` — the source-of-truth tab
- `dashboard` — KPIs and charts
- `config` — dropdown lists, enums
- `archive` — soft-deleted or historical

### C.3 — Column names
- `snake_case`, lowercase, no spaces.
- Foreign keys: `<entity>_id` → `employee_id`, `vendor_id`.
- Booleans: `is_*` or `has_*` → `is_active`, `has_returned`.
- Timestamps: `*_at` → `created_at`, `shipped_at`.
- Dates: `*_date` → `joining_date`, `due_date`.

---

## D. The visual system

This is what makes the Instagram content compelling. Every tracker follows the same look.

### D.1 — Category color palette

| Category | Hex | Header background |
|---|---|---|
| HR (`hr-*`) | `#10B981` | Emerald |
| Leadership (`lead-*`) | `#1F2937` | Slate-900 |
| R&D (`rnd-*`) | `#8B5CF6` | Violet |
| Procurement (`proc-*`) | `#0EA5E9` | Sky |
| Manufacturing (`mfg-*`) | `#F97316` | Orange |
| QC (`qc-*`) | `#EF4444` | Red |
| Inventory (`inv-*`) | `#EAB308` | Amber |
| Sales (`sales-*`) | `#A855F7` | Purple |
| Marketing (`mkt-*`) | `#EC4899` | Pink |
| Customer Support (`cs-*`, `cust-*`) | `#06B6D4` | Cyan |
| Finance (`fin-*`) | `#22C55E` | Green |
| Devices (`dev-*`) | `#6366F1` | Indigo |
| Admin (`admin-*`) | `#64748B` | Slate-500 |
| Catalog (`cat-*`) | `#78716C` | Stone |

Header row uses the category color (background) with white bold text.

### D.2 — Status pill formatting

Conditional formatting on any status column:

| Value | Background | Text |
|---|---|---|
| `OPEN` / `PENDING` | `#FEF3C7` (amber-100) | `#92400E` |
| `IN_PROGRESS` | `#DBEAFE` (blue-100) | `#1E40AF` |
| `DONE` / `COMPLETED` / `PASS` | `#D1FAE5` (green-100) | `#065F46` |
| `BLOCKED` / `FAIL` / `CRITICAL` | `#FEE2E2` (red-100) | `#991B1B` |
| `CANCELLED` / `ARCHIVED` | `#E5E7EB` (gray-200) | `#4B5563` |

Rounded look via cell padding + the wrap padding trick. Reads like a status pill.

### D.3 — KPI cards (top of every `dashboard` tab)

Top 3 rows of the dashboard tab show 3–5 big-number KPIs:
- Row 1: KPI label (small, gray)
- Row 2: Big number (size 24, bold)
- Row 3: Delta vs yesterday/last week (small, green if up, red if down)

Use merged cells for the big numbers. Background = category color at 10% opacity.

### D.4 — Typography

- Header row: bold, white, sans-serif (Arial / Roboto / Inter)
- Body: regular, dark gray (`#1F2937`)
- ID columns: monospace (Roboto Mono, JetBrains Mono)
- Numbers: tabular figures, right-aligned
- Dates: monospace, gray
- Currency: Indian Rupee, right-aligned, with grouping (`₹ 1,23,456`)

### D.5 — Layout rules

- Freeze the header row (and the ID column).
- Row height: 28px minimum.
- Zebra striping: alternate rows with `#F9FAFB` background.
- Padding: at least one blank column to the right of the data block.
- No gridlines on dashboard tab (turn off via View → Gridlines).

### D.6 — Charts

- Sparklines in summary rows (e.g., last-7-day mini-chart).
- Bar charts for category breakdowns.
- Line charts for trends.
- No 3D, no pie charts (except very simple two-slice).
- Chart colors pull from the category palette.

### D.7 — Empty-state aesthetic

When a sheet is empty, the data tab shows a single message in a merged centered cell:
*"No data yet. First row will appear here."*

---

## E. The Master Registry

The single sheet that indexes all trackers.

### `master-registry`

Columns:
- `tracker_id` — the slug, e.g., `hr-attendance`
- `name` — human-readable name
- `category` — one of the categories from D.1
- `sheet_id` — Google Sheet ID
- `primary_tab` — usually `data`
- `owner` — employee_id responsible
- `description` — one-line
- `tier` — T1 / T2 / T3 / T4 (bootcamp priority)
- `is_active` — TRUE / FALSE

Claude Code reads this sheet first to discover what data exists.

---

## F. The standard tracker folder

Every tracker in this repo has a folder under `trackers/<tracker-id>/` containing:

```
trackers/hr-attendance/
├── schema.md              # Column-by-column spec, this design bible applied
├── sample-data.csv        # 20–50 rows of realistic seed data
├── visual-spec.md         # Color, formatting, layout decisions for this tracker
├── claude-tips.md         # How Claude should reason about this data
└── reel-script.md         # 30–60s Instagram script for the bootcamp content
```

This is the unit of work. Each new tracker = one folder = one Instagram reel = one bootcamp lesson.
