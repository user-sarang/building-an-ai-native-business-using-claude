# `hr-attendance` → payroll inputs (PF, ESI, LOP)

This doc explains how the attendance log becomes the **upstream input for monthly statutory payroll**. The actual PF / ESI / net-salary numbers are stored in `hr-payroll` (to be built); this tracker is the source.

## Why this matters

Indian statutory payroll has two recurring monthly computations:

- **EPF (Employees' Provident Fund)** — 12% of earned basic from employee, 12% from employer
- **ESI (Employees' State Insurance)** — 0.75% from employee + 3.25% from employer, on earned gross, **only if** monthly gross ≤ ₹21,000

Both depend on **earned salary**, not the offer-letter salary. Earned salary depends on **days actually worked**, which comes from the attendance log.

## The chain

```
hr-attendance        →  Days worked, LOP days per employee
                        (Claude computes from raw rows)

hr-employee-master   →  Salary structure: basic, HRA, special, gross
                        (built later)

  combined           →  Earned basic, earned gross, LOP deduction
                        (Claude computes month-end)

hr-payroll           →  EPF, ESI, TDS, net salary
                        (computed once, stored once, signed off)
```

## Status → working-day weight

For payroll purposes, each attendance status converts as follows:

| status | counts as | notes |
|---|---|---|
| `PRESENT` | 1.0 day | normal working day |
| `WFH` | 1.0 day | same as present |
| `HALF_DAY` | 0.5 day | half a day worked |
| `LEAVE` | 1.0 day **if paid leave** | depends on leave type — see below |
| `LEAVE` | 0.0 day **if LOP (loss of pay)** | counts as LOP |
| `ABSENT` | 0.0 day | always LOP |
| `HOLIDAY` | 1.0 day | paid holiday, included in earning days |

> **Leave-type ambiguity**: this sheet stores only `LEAVE` as a single status. Whether a given leave row is paid (CL/SL/EL) or LOP depends on the employee's leave balance. That distinction lives in `hr-leave` (a separate tracker). For now, Claude assumes `LEAVE` = paid unless `hr-leave` says otherwise.

## Monthly aggregation per employee

For a given month M and employee E, Claude computes:

```
total_calendar_days(M)        = days in M
total_working_days(M)         = days in M with weekday() ≤ 5 (Mon–Sat for 6-day week)
total_paid_days_for_E(M, E)   = sum of weights from the table above, over rows
                                 where date ∈ M and employee_id = E
lop_days_for_E(M, E)          = total_working_days(M) − total_paid_days_for_E(M, E)
```

## Salary derivation (when hr-employee-master is in)

Given `monthly_basic`, `monthly_gross`, `monthly_hra`, `monthly_special` from `hr-employee-master`:

```
earned_basic    = monthly_basic    × (paid_days / total_working_days_in_M)
earned_hra      = monthly_hra      × (paid_days / total_working_days_in_M)
earned_special  = monthly_special  × (paid_days / total_working_days_in_M)
earned_gross    = earned_basic + earned_hra + earned_special
lop_deduction   = monthly_gross − earned_gross
```

## EPF computation

```
epf_wage_base   = min(earned_basic + earned_da, 15000)
                   # ₹15,000 statutory wage ceiling (PF Act)
                   # Many employers contribute on actual basic above ₹15k;
                   # store that policy per employee in hr-employee-master.

epf_employee    = 12% × epf_wage_base
epf_employer    = 12% × epf_wage_base    # of which 8.33% to EPS, 3.67% to EPF
```

## ESI computation

```
if monthly_gross ≤ 21000:                # ESI applicability threshold
    esi_employee = 0.75% × earned_gross
    esi_employer = 3.25% × earned_gross
else:
    esi_employee = 0
    esi_employer = 0
```

ESI applicability is decided based on the **offer-letter monthly gross**, not earned. Once applicable in a contribution period (Apr–Sep / Oct–Mar), it stays applicable for that period even if salary later rises.

## What Claude can answer purely from `hr-attendance`

Without needing `hr-employee-master` or `hr-payroll`, Claude can already answer:

- "How many days did `<name>` work in May?"
- "Who has LOP days this month?"
- "Total LOP days across the team this month?"
- "Which employees were absent without leave this month?"
- "Show me the May attendance summary, employee-wise"

Sample output for *"May attendance summary"*:

```
May 2026 attendance — 26 working days

employee_id   name              paid_days   lop_days   late_days
EMP-001       Arjun Mehta            26.0          0          2
EMP-003       Rohan Iyer             24.0          0          5    (WFH-heavy)
EMP-005       Vikram Singh           25.0          0          0    (1 sick day)
EMP-012       Ananya Gupta           23.0          3          4    ⚠️ 3 ABSENT
EMP-017       Sandeep Bhat           23.0          0          0    (3-day brother's wedding leave)
EMP-020       Ritu Aggarwal          21.0          0          0    (5-day EL Goa)
...
```

This becomes the input HR-admin uses on the 1st of the next month to compute payroll, with `hr-employee-master` providing the salary structure.

## Next trackers needed to close the loop

To go from this attendance log all the way to a payroll output, we need two more trackers:

1. **`hr-employee-master`** — salary structure per employee (basic, HRA, special, gross, PF policy, ESI eligibility)
2. **`hr-payroll`** — monthly computed row per employee (paid days, LOP, earned salary, EPF, ESI, TDS, net)
3. **`hr-leave`** (optional but cleaner) — to disambiguate paid leave vs LOP

Once these three exist, the full month-end payroll demo runs entirely on Claude reading the sheets and computing.
