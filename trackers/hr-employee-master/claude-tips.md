# `hr-employee-master` — Claude tips

How Claude Code should reason about this tracker when invoked.

## What this tracker answers

**Org / identity:**
- "Who is Arjun?" / "What does Priya do?"
- "Who reports to Vikram?"
- "Show me the R&D team."
- "How many people are in the factory?"
- "Who joined this month?"
- "Anyone on a 3-month tenure mark this week?"
- "Who's our newest hire?"

**Compensation / payroll prep:**
- "What's Rohan's monthly gross?"
- "Which employees are ESI-applicable?"
- "What's our total monthly payroll outlay?"
- "Annual salary cost for the manufacturing team?"

**Active / inactive:**
- "Has anyone left in the last 6 months?"
- "Who exited the company?"

## What this tracker does NOT answer

- Day-to-day attendance → `hr-attendance`
- Leave balances → `hr-leave` (future)
- Actual monthly payroll computation (PF, ESI, TDS, net) → `hr-payroll` (future)
- 1:1 / performance notes → `hr-one-on-ones` (future)
- Why someone left → `hr-offboarding` (future)

## Key reasoning rules

1. **Always filter by `is_active = TRUE`** when answering questions about "the team", "headcount", "everyone", unless the question explicitly asks about past employees.
2. **`reporting_manager_id` is recursive** — to find someone's full team, do a recursive search down the tree.
3. **The founder has blank `reporting_manager_id`** — that's the top of the tree, not an error.
4. **`monthly_gross` should equal `monthly_basic + monthly_hra + monthly_special`.** If it doesn't, flag a data integrity warning to the founder but use `monthly_gross` as the source of truth.
5. **`esi_applicable = TRUE` is set when monthly_gross ≤ ₹21,000.** Sanity-check this on read: if an employee's `monthly_gross > 21000` but `esi_applicable = TRUE`, ask whether it's a recent raise that hasn't taken effect this ESI period (Apr–Sep or Oct–Mar).
6. **PAN, UAN, bank_account, bank_ifsc are sensitive.** Default behavior: NEVER include these in casual responses. Only surface them when:
   - The founder explicitly asks ("show me Arjun's PAN"), or
   - The query is unambiguously about payroll / banking / statutory filings.

## Useful pre-computed queries

```
Headcount (active)        = COUNT(rows where is_active = TRUE)
Headcount per department  = GROUP BY department, COUNT where is_active = TRUE
Total monthly payroll     = SUM(monthly_gross) where is_active = TRUE
Annual payroll outlay     = SUM(monthly_gross) × 12 where is_active = TRUE
ESI-applicable count      = COUNT where esi_applicable = TRUE AND is_active = TRUE
Team of <manager_id>      = ROWS where reporting_manager_id = <manager_id>
                           (recurse for full subtree)
Tenure of <emp_id>        = TODAY() - joining_date
```

## Output format examples

### "Who's in the R&D team?"

```
R&D — 2 active members

EMP-003  Rohan Iyer       Firmware Engineer    WFH      ₹1.20L/mo
EMP-004  Neha Reddy       Hardware Engineer    OFFICE   ₹1.30L/mo

Both report to Priya (EMP-002, COO).
Total R&D cost: ₹2.50L/month  (₹30L/year)
```

### "What's our headcount and payroll?"

```
Active headcount: 20

LEADERSHIP        2     ₹3.80L
RND               2     ₹2.50L
MANUFACTURING     6     ₹1.75L
SUPPLY_CHAIN      2     ₹0.63L
SALES             3     ₹1.90L
MARKETING         2     ₹0.95L
SUPPORT           1     ₹0.30L
FINANCE           1     ₹0.50L
HR                1     ₹0.40L

Total monthly gross: ₹12.73L
Annual outlay:        ₹1.53Cr

ESI-applicable: 4 employees (all in MANUFACTURING / SUPPLY_CHAIN)
```

### "Who joined in 2022?"

```
2022 joiners — 5 people

EMP-013  Rahul Verma      B2B Sales Manager     joined 2022-01-20  (4.4 yrs)
EMP-008  Sneha Patil      Assembly Operator     joined 2022-02-14
EMP-020  Ritu Aggarwal    Finance Officer       joined 2022-03-07
EMP-009  Karthik Rao      Assembly Operator     joined 2022-05-30
EMP-014  Divya Menon      D2C Lead              joined 2022-06-12
```

## Edge cases

- **Inactive employee in a query**: if the founder asks "where is Rahul?" and Rahul is `is_active = FALSE`, explicitly say *"Rahul exited the company on `<exit_date>`."* Don't filter him out silently.
- **Self-reference in reporting tree**: Founder (`EMP-001`) has blank `reporting_manager_id`. Don't treat blank as a data error.
- **Tenure computations**: use `joining_date` to today's date. For exited employees, use `joining_date` to `exit_date`.
- **PII bleed-through**: even if Claude has the data, never echo bank/PAN in responses to ambiguous questions. Err on the side of "let me know if you specifically need PAN/bank info, otherwise I'll leave it out."

## Privacy posture

This is the most sensitive sheet in the Company OS:
- Full names, personal emails, personal phones — moderately sensitive
- PAN, UAN — sensitive (identity-theft potential)
- Bank account, IFSC — most sensitive (financial theft potential)
- Compensation — internally sensitive (cultural / fairness reasons)

When Claude responds:
- **Salary information**: only surface in payroll-context queries or when the founder explicitly asks. Never in casual team queries.
- **Bank details**: only in explicit payroll / banking queries. Never volunteer.
- **PAN / UAN**: only when the founder asks specifically for statutory / filing purposes.
- **Personal phone / email**: surface only if the question is clearly about contacting someone.

If the same query could be answered with or without sensitive fields, prefer without.
