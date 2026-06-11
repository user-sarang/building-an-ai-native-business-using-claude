# `hr-employee-master` — schema

The roster of every person who has ever worked at the company. The **master record** for identity, employment, statutory IDs, banking, and compensation structure.

**Category**: HR
**Tier**: T1 — built immediately after `hr-attendance` because attendance, payroll, leave, hiring, etc. all reference this sheet via `employee_id`.
**Type**: Master sheet (in-place edits, soft delete via `is_active`)
**Owner**: HR-admin
**Edit frequency**: When someone joins, exits, gets a raise, changes role, or updates bank/contact info. Daily? No. Monthly at most.
**Rows**: ~20 today; grows by ~5–10 per year for a 20-person co.

## Tab structure

**One tab only**: `data`. Same minimalist principle as `hr-attendance`. Fully manual.

## Columns (24)

Grouped by purpose. Letter = column in the sheet.

### Identity (A–C)
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `employee_id` | Text | yes | Primary key, format `EMP-NNN`. Immutable. |
| B | `full_name` | Text | yes | Legal name as on PAN |
| C | `preferred_name` | Text | yes | What colleagues call them — e.g. "Arjun" |

### Employment (D–K)
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| D | `role` | Text | yes | Job title, e.g. "Production Lead" |
| E | `department` | Enum dropdown | yes | See enum below |
| F | `reporting_manager_id` | Text (FK to A) | conditional | `employee_id` of manager. Blank only for founder. |
| G | `joining_date` | Date | yes | `YYYY-MM-DD` |
| H | `employment_type` | Enum dropdown | yes | `FULL_TIME` / `CONTRACT` / `INTERN` |
| I | `work_location` | Enum dropdown | yes | Default location for attendance: `OFFICE` / `FACTORY` / `WFH` / `FIELD` |
| J | `is_active` | Enum dropdown | yes | `TRUE` / `FALSE` |
| K | `exit_date` | Date | conditional | Required if `is_active = FALSE` |

### Contact (L–M)
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| L | `personal_email` | Text | yes | Personal Gmail / Outlook etc. |
| M | `personal_phone` | Text | yes | `+91XXXXXXXXXX` |

### Statutory IDs (N–O) — **SENSITIVE**
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| N | `pan_number` | Text | yes | Income-tax PAN, format `AAAAA9999A`. **Protected range** — restricted edit access. |
| O | `uan_number` | Text | yes (if PF applicable) | Universal Account Number for EPF — 12 digits |

> **Aadhaar is deliberately excluded.** Aadhaar is highly sensitive and storing it in a Google Sheet is a poor security posture. If needed for statutory filings, store separately in a restricted-access vault.

### Bank (P–R) — **SENSITIVE**
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| P | `bank_name` | Text | yes | e.g. "HDFC Bank" |
| Q | `bank_account` | Text | yes | Salary account number. **Protected.** |
| R | `bank_ifsc` | Text | yes | 11-char IFSC code |

### Compensation (S–V)
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| S | `monthly_basic` | Number (INR) | yes | Basic salary component |
| T | `monthly_hra` | Number (INR) | yes | House Rent Allowance |
| U | `monthly_special` | Number (INR) | yes | Special allowance (residual) |
| V | `monthly_gross` | Number (INR) | yes | Sum of S+T+U. **Typed manually** — HR enters once, treated as source. Sanity-check on read. |

### Statutory policy (W–X)
| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| W | `pf_applicable` | Enum dropdown | yes | `TRUE` / `FALSE`. Almost always TRUE for full-time employees. |
| X | `esi_applicable` | Enum dropdown | yes | `TRUE` / `FALSE`. `TRUE` when `monthly_gross ≤ 21000`. HR sets explicitly (not auto-derived). |

## Enums

### `department` (col E)
| Value | Meaning |
|---|---|
| `LEADERSHIP` | Founder, COO, etc. |
| `RND` | R&D / Engineering |
| `MANUFACTURING` | Production floor + QC |
| `SUPPLY_CHAIN` | Procurement + warehouse |
| `SALES` | D2C + B2B + inside sales |
| `MARKETING` | Content + performance |
| `SUPPORT` | Customer support |
| `FINANCE` | Accounts + finance |
| `HR` | HR + admin |

### `employment_type` (col H)
`FULL_TIME` · `CONTRACT` · `INTERN`

### `work_location` (col I)
`OFFICE` · `FACTORY` · `WFH` · `FIELD`

### `is_active` (col J)
`TRUE` · `FALSE`

### `pf_applicable` / `esi_applicable` (cols W, X)
`TRUE` · `FALSE`

## Validation rules

1. Column A (`employee_id`): protected, only HR-admin edits.
2. Column E, H, I, J, W, X: Data Validation → Dropdown (chip) with the enum values.
3. Column F (`reporting_manager_id`): Data Validation → Dropdown (chip) → range = `A2:A` of this sheet (self-referencing). Blank is also valid for founder.
4. Column G (`joining_date`): Data Validation → Date.
5. Column K (`exit_date`): Data Validation → Date. Required iff `is_active = FALSE`.
6. Column L: Data Validation → text contains `@`.
7. Column N (`pan_number`): Data Validation → custom regex `^[A-Z]{5}[0-9]{4}[A-Z]$`.

## Audit / history

Google Sheets version history (File → Version History). For a master sheet where edits are infrequent, this is sufficient and gives you "who changed Arjun's salary on March 14".

## Privacy & access

This sheet contains **PII and bank details**. Treatment:

- **Restrict edit access** to HR-admin and founder only.
- **Restrict view access** to: HR-admin, founder, finance (for payroll runs).
- **Protect ranges** on cols N (PAN) and Q (bank_account) so even viewers can't accidentally see them unless they have explicit access.
- When Claude Code surfaces info, **never expose bank account or PAN in chat output** unless the founder explicitly asks (and the prompt is clearly about payroll/banking, not casual queries like "what's Arjun's role").

## Relationships

| Tracker | How it references this | Cardinality |
|---|---|---|
| `hr-attendance` | `employee_id` foreign key | 1 → many (one employee, many rows) |
| `hr-leave` (future) | `employee_id` FK | 1 → many |
| `hr-payroll` (future) | `employee_id` FK | 1 → many (one row per employee per month) |
| `hr-one-on-ones` (future) | `employee_id` FK | 1 → many |
| `hr-asset-assignment` (future) | `employee_id` FK | 1 → many |
| `hr-employee-master` (self) | `reporting_manager_id` → `employee_id` | many → 1 (org tree) |

## Growth & archival

- Active count: ~20 today
- Total rows (including past employees): grows ~10/year
- Inactive employees stay in the sheet with `is_active = FALSE` and `exit_date` filled — never deleted. Allows historical queries ("who was the QC inspector in 2024?").
- Archive policy: none needed. Sheet stays ≪ 1000 rows for decades.
