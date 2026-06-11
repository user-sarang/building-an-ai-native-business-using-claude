# `hr-employee-master` — visual spec

The look. Same emerald HR theme as `hr-attendance`, but with **column grouping** because 24 columns benefits from visual structure. No formulas; everything below is typography, color, conditional formatting, or data validation.

## Category color
HR → **Emerald `#10B981`**

## Sheet setup

- **One tab**: `data`
- **Sheet name**: `hr-employee-master`
- Trim unused columns beyond X to keep the sheet visually bounded.
- Trim unused rows beyond row 50 (master sheets stay small).

## Header row (row 1)

Two-row header for grouping:

### Row 1 — group bands (merged cells, lighter shade)
| Range | Label | Background |
|---|---|---|
| A1:C1 | IDENTITY | `#065F46` (emerald-800) |
| D1:K1 | EMPLOYMENT | `#0D9488` (teal-600) |
| L1:M1 | CONTACT | `#475569` (slate-600) |
| N1:O1 | STATUTORY IDs 🔒 | `#B91C1C` (red-700) |
| P1:R1 | BANK 🔒 | `#1D4ED8` (blue-700) |
| S1:V1 | COMPENSATION | `#A16207` (amber-700) |
| W1:X1 | STATUTORY POLICY | `#6D28D9` (violet-700) |

All white bold text, size 10, centered. Each band is a merged cell across that group's columns. The 🔒 emoji on sensitive group bands is intentional.

### Row 2 — column headers
| Range | Background |
|---|---|
| A2:X2 | `#10B981` (emerald-500) |

White bold text, size 11, left-aligned, frozen.

Frozen: View → Freeze → 2 rows, 1 column.

## Column widths

| Col | Header | Width |
|---|---|---|
| A | `employee_id` | 90 px |
| B | `full_name` | 180 px |
| C | `preferred_name` | 110 px |
| D | `role` | 200 px |
| E | `department` | 130 px |
| F | `reporting_manager_id` | 110 px |
| G | `joining_date` | 110 px |
| H | `employment_type` | 110 px |
| I | `work_location` | 100 px |
| J | `is_active` | 90 px |
| K | `exit_date` | 110 px |
| L | `personal_email` | 220 px |
| M | `personal_phone` | 140 px |
| N | `pan_number` | 120 px |
| O | `uan_number` | 130 px |
| P | `bank_name` | 130 px |
| Q | `bank_account` | 170 px |
| R | `bank_ifsc` | 120 px |
| S | `monthly_basic` | 110 px |
| T | `monthly_hra` | 110 px |
| U | `monthly_special` | 110 px |
| V | `monthly_gross` | 120 px |
| W | `pf_applicable` | 100 px |
| X | `esi_applicable` | 100 px |

## Body rows

| Setting | Value |
|---|---|
| Font | Inter (fallback: Arial), size 10 |
| Text color | `#1F2937` (slate-800) |
| Row height | 32 px (slightly taller — readable for a reference table) |
| Zebra striping | Alternate `#FFFFFF` / `#F9FAFB` |

## Column-specific formatting

### A. `employee_id`
- Font: JetBrains Mono / Roboto Mono, size 10
- Color: `#475569`
- Background: `#ECFDF5` (very subtle emerald tint to mark the primary key column)

### B. `full_name`, C. `preferred_name`
- Font: Inter, size 10
- B: weight 500 (semi-bold)
- C: regular

### D. `role`
- Font: Inter, size 10, weight 500

### E. `department` — conditional formatting pills

| Value | Background | Text |
|---|---|---|
| `LEADERSHIP` | `#1F2937` | `#FFFFFF` |
| `RND` | `#EDE9FE` | `#5B21B6` |
| `MANUFACTURING` | `#FFEDD5` | `#9A3412` |
| `SUPPLY_CHAIN` | `#E0F2FE` | `#0369A1` |
| `SALES` | `#FAE8FF` | `#86198F` |
| `MARKETING` | `#FCE7F3` | `#9D174D` |
| `SUPPORT` | `#CFFAFE` | `#155E75` |
| `FINANCE` | `#DCFCE7` | `#166534` |
| `HR` | `#D1FAE5` | `#065F46` |

Each department gets its own pill color — pulled from the category palette in the design bible. Reads at-a-glance.

### F. `reporting_manager_id`
- Font: JetBrains Mono / Roboto Mono, size 10
- Color: `#64748B`

### G, K. `joining_date`, `exit_date`
- Format: `yyyy-mm-dd`
- Font: Roboto Mono, size 10
- Color: `#475569`

### H. `employment_type` — pills
| Value | Background | Text |
|---|---|---|
| `FULL_TIME` | `#D1FAE5` | `#065F46` |
| `CONTRACT` | `#FEF3C7` | `#92400E` |
| `INTERN` | `#DBEAFE` | `#1E40AF` |

### I. `work_location` — pills (same colors as in hr-attendance)
| Value | Background | Text |
|---|---|---|
| `OFFICE` | `#E5E7EB` | `#374151` |
| `FACTORY` | `#FFEDD5` | `#9A3412` |
| `WFH` | `#DBEAFE` | `#1E40AF` |
| `FIELD` | `#FAE8FF` | `#86198F` |

### J. `is_active` — pills
| Value | Background | Text |
|---|---|---|
| `TRUE` | `#D1FAE5` | `#065F46` |
| `FALSE` | `#FEE2E2` | `#991B1B` |

### L. `personal_email`
- Font: Inter, size 10
- Color: `#3B82F6` (link blue), underline on hover
- Truncate on overflow

### M. `personal_phone`
- Font: Roboto Mono, size 10

### N, O. Statutory IDs — sensitive
- Font: Roboto Mono, size 10
- Color: `#64748B`
- Background tint: very subtle red `#FEF2F2` for the *whole column body* (faint warning visual)
- **Protected range**: only HR-admin can view/edit. Other viewers see "•••••" (use Sheets' protected-range "show warning" mode, or hide the column for non-HR viewers).

### P, Q, R. Bank — sensitive
- Font: Roboto Mono, size 10
- Color: `#64748B`
- Background tint: very subtle blue `#EFF6FF` for the column body
- **Protected range**: same restriction as statutory IDs.

### S, T, U, V. Compensation columns
- Format: Currency → `₹#,##,##0` (Indian numbering with lakhs/crores grouping)
- Font: Roboto Mono, size 10
- Right-aligned
- Background tint: very subtle amber `#FFFBEB` for the column body
- **Protected range**: HR-admin + founder only.

### V. `monthly_gross` (special)
- Same as above
- **Bold** — it's the headline compensation number
- Add a sanity-check conditional format: if `V ≠ S + T + U`, highlight with red border. (This is a visual check via conditional formatting, not a formula in the cell.)

### W, X. Statutory policy — pills
Same green/red TRUE/FALSE pill style as column J.

## Freezing

- Freeze top 2 rows (group band + headers).
- Freeze column A (employee_id) — useful since the sheet is wide.

## Data validation

1. Cols E, H, I, J, W, X: Dropdown (chip) with enum values from `schema.md`.
2. Col F (`reporting_manager_id`): Dropdown referencing range `A3:A` (self-FK).
3. Cols G, K: Date validation.
4. Col L: Text contains `@`.
5. Col N: Custom regex `^[A-Z]{5}[0-9]{4}[A-Z]$`.
6. Cols S–V: Number validation, min 0.

## What this looks like at a glance

```
              ╔════ IDENTITY ════╗╔═══════════════ EMPLOYMENT ═══════════════╗╔══ CONTACT ══╗╔ STATUTORY IDs 🔒 ╗╔══════ BANK 🔒 ══════╗╔═══════ COMPENSATION ═══════╗╔ POLICY ══╗
              ┌──────┬──────────┬┬────────┬────┬──────┬────────┬────────┬───┬┬─────┬───────┬┬─────────┬────────┬┬─────┬──────┬─────┬┬────────┬──────┬──────┬───────┬┬─────┬─────┐
   employee_id│ full │preferred │ role   │dept│ mgr  │ joined │ type   │loc│active│ exit │ email   │  phone  │ PAN  │ UAN  │bank │acc#│ ifsc│ basic │ hra │special│gross │ pf │ esi │
              ├──────┼──────────┼┼────────┼────┼──────┼────────┼────────┼───┼┼─────┼───────┼┼─────────┼────────┼┼─────┼──────┼─────┼┼────────┼──────┼──────┼───────┼┼─────┼─────┤
   EMP-001    │Arjun │ Arjun    │Founder │▒LD▒│      │2019-04 │ FT     │OFC│ TRUE │       │ arjun@..│ +91...  │ AKJ..│100.. │HDFC │501..│HDFC.│ 100000│ 50000│ 50000│200000 │TRUE │FALSE│
   EMP-002    │Priya │ Priya    │COO     │▒LD▒│EMP-01│2020-02 │ FT     │OFC│ TRUE │       │ priya@..│ +91...  │ BLK..│100.. │HDFC │501..│HDFC.│  90000│ 45000│ 45000│180000 │TRUE │FALSE│
   EMP-007    │Aditya│ Aditya   │Op      │▒MF▒│EMP-05│2021-07 │ FT     │FAC│ TRUE │       │ aditya@.│ +91...  │ GHK..│100.. │CNRB │150..│CNRB.│  10000│  5000│  5000│ 20000 │TRUE │ TRUE│  ← ESI applies
              └──────┴──────────┴┴────────┴────┴──────┴────────┴────────┴───┴┴─────┴───────┴┴─────────┴────────┴┴─────┴──────┴─────┴┴────────┴──────┴──────┴───────┴┴─────┴─────┘
                   ↑ identity         ↑ employment band (teal)    ↑ contact    ↑ red tint (sensitive)  ↑ blue tint (bank)    ↑ amber tint (₹)    ↑ violet
```

The colored department pills (`▒LD▒`, `▒MF▒`, etc.) and column-body tints give the sheet a layered, professional feel.

## Sensitive column treatment (protected ranges)

In Google Sheets:
1. Select range N:O (statutory IDs)
2. Data → Protected sheets and ranges → Add a sheet/range
3. Restrict editors to HR-admin + founder
4. (Optionally) for non-permitted viewers, hide the column entirely

Repeat for Q (bank_account). Q is the most sensitive single cell in the entire Company OS.

The visual red/blue tints serve as a **warning before you even read the column** that this is sensitive data.

## Instagram angle

- Reel: *"24 columns. 9 departments. 4 sensitive groups. The cleanest employee master sheet for an Indian product company."*
- Show the **department pill** rapid-fire as you click through dropdowns (LEADERSHIP → R&D → MFG → etc., colors flashing).
- Then show the **sensitive column tints** with a 🔒 emoji floating in to call out PII handling.
- Punchline: *"Your founder gets one source of truth for every person in the company. Claude reads it. Payroll uses it. HR maintains it."*
