# `hr-attendance` — Claude tips

How Claude Code should reason about this tracker when invoked.

## What this tracker answers

**Today / near-term:**
- "Who is in today?"
- "Who's absent today / yesterday?"
- "How many people are working from home?"
- "Did `<name>` come in yesterday?"
- "Show me attendance for the factory team today."

**Month-end / payroll:**
- "How many days did `<name>` work this month?"
- "Who has LOP days this month?" (Loss of Pay)
- "Give me the May attendance summary for payroll."
- "Total paid days vs LOP days across the team this month?"
- "Which employees are at risk of triggering disciplinary action?" (3+ ABSENT)

For the full payroll mapping (PF, ESI, earned salary), see `payroll-inputs.md`.

## What this tracker does NOT answer

- Leave balances → that's `hr-leave`
- Payroll → that's `hr-payroll`
- Why someone left the company → not tracked here, see `hr-offboarding`

If a question requires those, Claude should call the relevant skill, not infer from attendance alone.

## Key reasoning rules

1. **"Today" means IST date** — convert to `Asia/Kolkata` before comparing.
2. **`PRESENT` and `WFH` both count as working.** Don't report someone as absent because they were WFH.
3. **`HALF_DAY` counts as 0.5** when computing attendance %.
4. **`HOLIDAY` rows are excluded** from attendance % calculations (denominator).
5. **`ABSENT` is different from `LEAVE`.** Absent = no-show. Leave = approved. Don't conflate.
6. **Field staff (`location=FIELD`)** are working. Sales reps on site visits should be reported as present.

## Useful queries (Claude computes these from the raw 8 columns)

The sheet stores only raw fields. Claude derives everything else on the fly:

```
Present today    = COUNT(rows where date=TODAY() AND status IN [PRESENT, WFH])
Half-day today   = COUNT(rows where date=TODAY() AND status=HALF_DAY)
Absent today     = COUNT(rows where date=TODAY() AND status=ABSENT)
On leave today   = COUNT(rows where date=TODAY() AND status=LEAVE)
Late today       = COUNT(rows where date=TODAY() AND check_in > '09:30')
Hours worked     = check_out - check_in (for any row, computed on demand)
Late minutes     = MAX(0, check_in - '09:30') in minutes (computed on demand)
Attendance % MTD = working_rows / non_holiday_rows over current month
```

No columns store these. Claude computes from the 8 raw columns when asked.

## Output format

When the founder asks "How is attendance today?", respond like:

```
Today (2026-06-01) — 18 of 20 working

PRESENT  14   (incl. 2 WFH, 1 field visit)
HALF_DAY  1   Meera
LEAVE     2   Neha (casual), Ritu (EL till Wed)
ABSENT    1   Ananya — no call no show ⚠️
LATE      3   Manish (10m), Suresh (5m), Pooja (30m, WFH/dr appt)
```

Keep it scannable. Bold the exceptions (absent, very late). The founder should be able to act on this in 5 seconds.

## Edge cases

- **Mid-month employee join**: only count attendance from their `joining_date` (from `hr-employee-master`).
- **Inactive employees**: filter by `hr-employee-master.is_active = TRUE` before computing %.
- **Future-dated rows** (planned leave): show in summary as "upcoming leave" if asked, never count as today's attendance.
- **Missing check_out** (forgot to log): flag as "not yet logged out" rather than treating as 0 hours.

## Privacy

Attendance is sensitive. Default behaviour:
- Answers to the founder include names freely.
- If a skill is invoked in a context where it might surface to non-HR users (future), default to anonymized counts ("18 present, 1 absent") unless explicitly asked for names.
