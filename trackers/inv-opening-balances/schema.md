# `inv-opening-balances` — schema

The **cutover baseline** for finished-goods stock. One row per SKU, recording how many units were on hand on a fixed `as_of_date`. The recompute engine starts here and adds every movement after the cutover to arrive at current stock — exactly like `hr-leave-opening-balances` seeds the leave engine.

**Category**: Inventory (`inv-*`, header color Amber `#EAB308`)
**Tier**: T1 (foundational, week 1)
**Type**: Master / input sheet (set once at cutover; rarely edited afterward)
**Owner**: Warehouse & Dispatch (`EMP-012`, Ananya), signed off by Finance (`EMP-020`, Ritu)

## Why this exists

You can't recompute "current stock = opening + ins − outs" without an opening. Rather than log a movement for every unit that existed before you started this system, you take one physical count on a cutover date and record it here. From that day forward, the `inv-stock-movement` ledger carries every change. To re-baseline later (e.g. fiscal year-end), set a new `as_of_date` and counts, and archive movements before it.

## Tab structure

**One tab**, `data`.

## Columns (5)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `sku_id` | Text (FK → `inv-finished-goods`) | yes | Primary key. e.g. `AQM-PRO-01`. Monospace. |
| B | `as_of_date` | Date | yes | Cutover date the count was taken. `YYYY-MM-DD`. Same for all rows in a baseline. |
| C | `opening_qty` | Number | yes | Physical units on hand at cutover (≥ 0) |
| D | `unit_cost` | Number (INR) | no | Cost per unit at cutover, for opening valuation |
| E | `notes` | Text | no | Free text — e.g. "physical count, store A" |

## Validation rules

1. `sku_id` (A): unique; one opening per SKU per baseline.
2. `opening_qty` (C): Number → ≥ 0.
3. `as_of_date` (B): Date validation.

## Relationships

| Tracker | References via | Role |
|---|---|---|
| `inv-finished-goods` | `sku_id` | the SKU whose balance is being seeded |
| `inv-stock-movement` | movements dated **after** `as_of_date` are summed onto the opening | engine input |

## Recompute rule

`qty_on_hand(today) = opening_qty + Σ(IN movements after as_of_date) − Σ(OUT movements after as_of_date)`

The engine recomputes this on every run, so the live snapshot always reflects opening plus the full movement history — no incremental patching.
