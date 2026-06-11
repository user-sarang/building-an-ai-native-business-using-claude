# Sources of Truth — the 80+ trackers

Every datum the company captures lives in exactly one tracker. This is the master list.

Each tracker becomes one Google Sheet (or one tab within a category sheet). Each tracker eventually gets one or more Claude Code skills built on top of it.

## Numbering
Trackers are referenced by `[category-prefix]-[noun]` throughout the repo.

---

## 1. People & Org (HR)
1. `hr-employee-master` — name, role, DOJ, salary, PAN, Aadhaar, UAN, ESI, bank details
2. `hr-attendance` — daily in/out, per employee
3. `hr-leave` — leave requests + balances (CL/SL/EL/LOP)
4. `hr-payroll` — monthly: gross, PF, ESI, TDS, net
5. `hr-hiring-pipeline` — open roles, candidates, stages
6. `hr-onboarding` — new joiner checklist
7. `hr-one-on-ones` — 1:1 / performance review notes
8. `hr-asset-assignment` — laptops, ID cards, SIM cards
9. `hr-offboarding` — exit checklist

## 2. Strategy & Leadership
10. `lead-okrs` — quarterly OKRs per function
11. `lead-decisions` — decisions log
12. `lead-risks` — risk register
13. `lead-board-updates` — investor / board update log

## 3. R&D
14. `rnd-project-pipeline` — idea → prototype → pilot → launch
15. `rnd-bom-master` — BOM per product per version
16. `rnd-component-eval` — vendor samples tested
17. `rnd-prototype-tests` — test results
18. `rnd-calibration-master` — sensor calibration reference data
19. `rnd-firmware-versions` — firmware version history + changelog
20. `rnd-ip-log` — patents and IP filings

## 4. Supply Chain & Procurement
21. `proc-vendor-master` — vendor name, GSTIN, terms, lead time, contact
22. `proc-component-master` — SKU master: part no., spec, MOQ, current vendor
23. `proc-purchase-orders` — PO log
24. `proc-grn` — goods received note log
25. `proc-imports` — China import shipment tracker
26. `proc-vendor-performance` — on-time delivery, defect rate per vendor

## 5. Manufacturing & QC
27. `mfg-production-plan` — weekly plan
28. `mfg-daily-production` — units per station per shift
29. `mfg-wip` — work-in-progress tracker
30. `mfg-downtime` — equipment / line downtime log
31. `qc-iqc` — incoming component quality
32. `qc-final` — per-unit pass/fail with serial number
33. `qc-defects` — defect categorization
34. `mfg-equipment-maintenance` — equipment maintenance log

## 6. Inventory & Warehouse
35. `inv-components` — component stock (live)
36. `inv-finished-goods` — AQI units + speakers
37. `inv-stock-movement` — every in/out log
38. `inv-dispatch` — orders shipped today
39. `inv-returns` — returns inward log

## 7. Sales — D2C
40. `sales-d2c-orders` — daily orders from Shopify + Amazon
41. `sales-d2c-channel` — channel performance summary
42. `sales-d2c-returns` — cancellations & returns
43. `sales-d2c-coupons` — discount / coupon usage

## 8. Sales — B2B
44. `sales-b2b-pipeline` — lead → qualified → proposal → won/lost
45. `sales-b2b-quotations` — quotations sent log
46. `sales-b2b-accounts` — corporate / school / hospital master
47. `sales-b2b-activity` — calls, demos, site visits

## 9. Marketing
48. `mkt-content-calendar` — Instagram, YouTube planned + posted
49. `mkt-content-performance` — reach, engagement per post
50. `mkt-ad-campaigns` — Meta + Google: spend, conversions
51. `mkt-utms` — link & UTM tracker
52. `mkt-influencers` — influencer / collab log
53. `mkt-emails` — email campaign log
54. `mkt-seo` — keyword & ranking tracker

## 10. Customer & Support
55. `cust-master` — customer master (D2C + B2B)
56. `cs-tickets` — support ticket log
57. `cs-rma` — RMA log
58. `cs-warranty` — warranty claims
59. `cs-nps` — NPS / feedback responses

## 11. Finance
60. `fin-cashflow` — daily cash position
61. `fin-bank` — bank statement log (per account)
62. `fin-ar` — accounts receivable
63. `fin-ap` — accounts payable
64. `fin-expenses` — categorized expense log
65. `fin-petty-cash` — petty cash log
66. `fin-gst-output` — sales GST register
67. `fin-gst-input` — purchase GST register
68. `fin-tds` — TDS log
69. `fin-reimbursements` — employee reimbursements
70. `fin-reconciliation` — bank reconciliation

## 12. Connected Device Data (the AQI in the field)
71. `dev-registry` — device serial → customer → DOA
72. `dev-telemetry` — daily telemetry summary per device
73. `dev-firmware-field` — firmware version distribution in the field
74. `dev-sensor-drift` — sensor drift trend per unit

## 13. Admin, Compliance & IT
75. `admin-asset-register` — office furniture, equipment
76. `admin-saas` — SaaS subscriptions: tool, owner, renewal, cost
77. `admin-compliance` — compliance calendar (GSTR-1/3B, PF, ESI, TDS, ROC)
78. `admin-insurance` — insurance policies (asset, health, liability)
79. `admin-credentials` — restricted credentials master

## 14. Product Catalog (cross-cutting)
80. `cat-sku-master` — SKU: name, MRP, cost, weight, dimensions
81. `cat-pricing-history` — pricing changes over time

---

## Master registry
A single sheet — `master-registry` — lists every tracker above with: sheet ID, owner, category, last updated. This is **the index** Claude Code uses to discover what data is available.

## Priority tiers for the bootcamp

To keep the curriculum sequenced, trackers are tiered:

- **T1 (foundational — week 1)**: `hr-attendance`, `mfg-daily-production`, `inv-finished-goods`, `sales-d2c-orders`, `fin-cashflow`
- **T2 (operational — week 2)**: `hr-employee-master`, `qc-final`, `inv-components`, `sales-b2b-pipeline`, `cs-tickets`, `fin-expenses`, `proc-purchase-orders`
- **T3 (advanced — week 3)**: R&D trackers, marketing, device telemetry, compliance
- **T4 (long tail — week 4 / post-bootcamp)**: remaining trackers, integrations, write-back actions

Each tracker takes the same workflow: design schema → apply visual system → populate sample data → build atomic skill → record reel.
