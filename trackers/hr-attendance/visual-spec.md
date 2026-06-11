# `hr-attendance` — visual spec

The look. Apply this to the actual Google Sheet so it matches the rest of the Company OS. Nothing here requires a formula — every rule below is either typography, color, or a conditional-formatting rule (which is built into Sheets, not a formula).

## Category color
HR → **Emerald `#10B981`**

## Sheet setup

- **One tab**: `data`
- **Sheet name**: `hr-attendance`
- **Hide gridlines beyond column H**: View → drag the boundary, or just delete unused columns to keep the sheet visually contained.

## Header row (row 1)

| Setting | Value |
|---|---|
| Background | `#10B981` (emerald) |
| Text color | `#FFFFFF` (white) |
| Font weight | Bold |
| Font size | 11 |
| Font family | Inter (fallback: Arial) |
| Row height | 36 px |
| Frozen | Yes — View → Freeze → 1 row |

Headers exactly: `date` · `employee_id` · `employee_name` · `status` · `check_in` · `check_out` · `location` · `notes`

## Column widths (suggested)

| Column | Width |
|---|---|
| A `date` | 110 px |
| B `employee_id` | 100 px |
| C `employee_name` | 180 px |
| D `status` | 110 px |
| E `check_in` | 90 px |
| F `check_out` | 90 px |
| G `location` | 100 px |
| H `notes` | 320 px |

## Body rows

| Setting | Value |
|---|---|
| Font | Inter (fallback: Arial), size 10 |
| Text color | `#1F2937` (slate-800) |
| Row height | 28 px |
| Zebra striping | Alternate `#FFFFFF` / `#F9FAFB` |

Zebra striping via **Format → Alternating colors** (built-in feature, not a formula). Pick the "Light gray" preset and customize header color to match emerald.

## Column-specific formatting

### A. `date`
- Format: Date → `2026-06-01` style → custom format `yyyy-mm-dd`
- Font: Roboto Mono, size 10
- Color: `#475569`
- Alignment: left

### B. `employee_id`
- Font: Roboto Mono, size 10
- Color: `#475569`
- Alignment: left

### C. `employee_name`
- Font: Inter, size 10
- Color: `#1F2937`
- Alignment: left

### D. `status` — the status pills
Conditional formatting (Format → Conditional formatting):

| Value (Text contains exactly) | Background | Text |
|---|---|---|
| `PRESENT` | `#D1FAE5` | `#065F46` |
| `WFH` | `#DBEAFE` | `#1E40AF` |
| `HALF_DAY` | `#FEF3C7` | `#92400E` |
| `LEAVE` | `#E0E7FF` | `#3730A3` |
| `ABSENT` | `#FEE2E2` | `#991B1B` |
| `HOLIDAY` | `#E5E7EB` | `#4B5563` |

All bold, centered. Reads like pill labels.

### E, F. `check_in`, `check_out`
- Format: Time → `13:25` style → custom format `HH:mm`
- Font: Roboto Mono, size 10
- Alignment: right

### G. `location`
- Font: Inter, size 10
- Alignment: center

### H. `notes`
- Font: Inter Italic, size 10
- Color: `#6B7280` (gray-500)
- Wrap: Wrap text on
- Alignment: left

## Freezing

- Freeze row 1 (header).
- Optionally freeze column A (date) — useful when scrolling far right with many days of data.

## Data validation (constraints, not formulas)

- **A `date`**: Data → Data validation → Criteria: Date is valid date. Reject input.
- **D `status`**: Data → Data validation → Criteria: Dropdown (chip). Items: `PRESENT, WFH, HALF_DAY, LEAVE, ABSENT, HOLIDAY`. Reject input on invalid.
- **G `location`**: Data → Data validation → Criteria: Dropdown (chip). Items: `OFFICE, FACTORY, WFH, FIELD, LEAVE`. Reject input on invalid.

## What this looks like at a glance

```
┌──────────────┬─────────────┬──────────────────┬───────────┬──────────┬───────────┬──────────┬─────────────────────────┐
│ date         │ employee_id │ employee_name    │ status    │ check_in │ check_out │ location │ notes                   │   ← emerald header
├──────────────┼─────────────┼──────────────────┼───────────┼──────────┼───────────┼──────────┼─────────────────────────┤
│ 2026-06-01   │ EMP-001     │ Arjun Mehta      │ ▒PRESENT▒ │ 09:25    │ 18:40     │ OFFICE   │                         │   ← white
│ 2026-06-01   │ EMP-002     │ Priya Sharma     │ ▒PRESENT▒ │ 09:32    │ 18:30     │ OFFICE   │                         │   ← gray-50
│ 2026-06-01   │ EMP-003     │ Rohan Iyer       │ ▒  WFH  ▒ │ 09:45    │ 19:10     │ WFH      │ Firmware v2.3 release   │   ← white
│ 2026-06-01   │ EMP-004     │ Neha Reddy       │ ▒ LEAVE ▒ │          │           │ LEAVE    │ Casual - family function│   ← gray-50
│ 2026-06-01   │ EMP-012     │ Ananya Gupta     │ ▒ABSENT ▒ │          │           │ LEAVE    │ No call no show         │
└──────────────┴─────────────┴──────────────────┴───────────┴──────────┴───────────┴──────────┴─────────────────────────┘
```

The `▒...▒` represents the colored status pill — green for PRESENT, red for ABSENT, blue for LEAVE/WFH, amber for HALF_DAY.

## What this looks like on Instagram

- **Before reel**: a participant's typical attendance sheet — random column order, no validation, mixed date formats, "P/A/L" free-text codes.
- **After reel**: this exact layout. Cuts between clicking the status dropdown and watching the pill flash green/red/amber.
- Hook line: *"Your HR sheet looks like 2007. Here's the 2026 version your founder will actually open."*
