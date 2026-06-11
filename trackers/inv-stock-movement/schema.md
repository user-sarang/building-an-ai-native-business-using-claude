# `inv-stock-movement` — schema

The **append-only ledger of every stock change** — one row per movement, in or out, for every finished-goods SKU. This is the engine behind the `inv-finished-goods` snapshot: that sheet shows the *balance*, this sheet records *how it got there*. Nothing edits stock silently — it posts a row here.

**Category**: Inventory (`inv-*`, header color Amber `#EAB308`)
**Tier**: T1 (foundational, week 1)
**Type**: Transaction sheet (append-only — never edit or delete a posted movement; correct with a reversing entry)
**Owner**: Warehouse & Dispatch (`EMP-012`, Ananya)
**Daily effort**: posted continuously as stock moves (a few seconds per event)

## The core idea: snapshot = opening + ins − outs

For any SKU, its current `qty_on_hand` in `inv-finished-goods` equals its opening balance plus every `IN` movement minus every `OUT` movement here. A small skill recomputes the snapshot from this ledger (the same recompute-from-history pattern your leave and payroll trackers already use), so a human never does the arithmetic and the snapshot can never silently drift.

Every other tracker is a *source* of movements:

| Source tracker | Posts | Direction |
|---|---|---|
| `mfg-daily-production` (PACKING done) | `PRODUCTION_IN` | IN |
| `proc-grn` (goods received) | `PURCHASE_IN` | IN |
| `sales-d2c-returns` / `cs-rma` | `SALES_RETURN_IN` | IN |
| `inv-dispatch` (order shipped) | `SALES_OUT` | OUT |
| damage / write-off | `SCRAP_OUT` | OUT |
| `inv-stock-count` (cycle count) | `ADJUSTMENT_IN` / `ADJUSTMENT_OUT` | IN/OUT |

## Tab structure

**One tab**, `data`. (Current balances live in `inv-finished-goods`; no dashboard needed here.)

## Columns (12)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `movement_id` | Text | yes | Primary key. Format `STM-YYYY-NNNNN`, e.g. `STM-2026-00001`. Immutable. Monospace. |
| B | `movement_date` | Date | yes | `YYYY-MM-DD` when the stock physically moved |
| C | `movement_type` | Enum (dropdown) | yes | The reason. See enum below — implies direction. |
| D | `direction` | Enum (dropdown) | yes | `IN` / `OUT`. Must agree with `movement_type`. Stored for fast filtering + the status pill. |
| E | `sku_id` | Text (FK → `inv-finished-goods`) | yes | Product moved, e.g. `AQM-PRO-01` |
| F | `product_name` | Text | yes | Denormalized readable name |
| G | `quantity` | Number | yes | Units moved — **always positive** (≥ 1). Direction carries the sign. |
| H | `reference_type` | Enum (dropdown) | yes | What document triggered it. See enum below. |
| I | `reference_id` | Text | conditional | The source doc ID (production/order/GRN/RMA/count). Blank only for `MANUAL`. |
| J | `handled_by` | Text (FK → `hr-employee-master`) | yes | `employee_id` who performed/logged the movement |
| K | `unit_cost` | Number (INR) | no | Cost per unit at time of movement — for valuation (IN) and COGS (OUT) |
| L | `notes` | Text | no | Free text — damage reason, count variance, etc. |

## Enums

### `movement_type` (column C) → implied `direction`

| Value | Direction | Meaning |
|---|---|---|
| `PRODUCTION_IN` | IN | Finished units from `mfg-daily-production` PACKING |
| `PURCHASE_IN` | IN | Traded goods received against a GRN (speakers, accessories) |
| `SALES_RETURN_IN` | IN | Customer return restocked as sellable |
| `SALES_OUT` | OUT | Dispatched against a customer order |
| `SCRAP_OUT` | OUT | Damaged / written off, removed from sellable stock |
| `ADJUSTMENT_IN` | IN | Cycle-count surplus (found stock) |
| `ADJUSTMENT_OUT` | OUT | Cycle-count shortage (missing stock) |

### `direction` (column D)
`IN` · `OUT` — conditional-formatting pill (green IN / red OUT, Design Bible §D.2).

### `reference_type` (column H)
| Value | Pairs with | Points at |
|---|---|---|
| `PRODUCTION` | `PRODUCTION_IN` | `mfg-daily-production.production_id` (the PACKING row) |
| `PURCHASE_GRN` | `PURCHASE_IN` | `proc-grn` receipt ID |
| `DISPATCH` | `SALES_OUT` | `sales-d2c-orders.order_id` (or `inv-dispatch` ID) |
| `SALES_RETURN` | `SALES_RETURN_IN` | RMA / `sales-d2c-returns` ID |
| `STOCK_COUNT` | `ADJUSTMENT_IN/OUT` | `inv-stock-count` session ID |
| `MANUAL` | `SCRAP_OUT` / ad-hoc | none (free `reference_id`) |

## Validation rules to set

1. Column A (`movement_id`): protected; unique. Never reused.
2. Columns C, D, H (`movement_type`, `direction`, `reference_type`): Data Validation → Dropdown.
3. `direction` must match `movement_type`'s implied direction (flag on read).
4. Column G (`quantity`): Number → ≥ 1.
5. Column B (`movement_date`): Date validation.
6. **No edits/deletes.** A wrong entry is corrected by posting an opposite-direction reversing movement, noted in `notes`.

## What's NOT stored (Claude computes on the fly)

- **Current `qty_on_hand`** per SKU — opening + Σ IN − Σ OUT. (Recomputed into `inv-finished-goods`.)
- **Running balance after each movement** — order-dependent; computed when needed.
- **Throughput** — units produced vs shipped over a period.
- **Inventory valuation movement** — `quantity × unit_cost` summed by direction.
- **Reconciliation** — ledger-derived balance vs the snapshot's stored `qty_on_hand` (drift alarm).

## Natural key

`movement_id` is the primary key. There is no other natural key — the same SKU moves many times a day; each event is its own immutable row.

## Audit / change history

The ledger **is** the audit trail for stock; `handled_by` records who moved it, and Google Sheets version history covers any accidental edit. Because rows are never modified after posting, the sheet is self-auditing.

## Relationships

| Tracker | References via | Cardinality |
|---|---|---|
| `inv-finished-goods` | `sku_id`; balances roll up | many → 1 |
| `hr-employee-master` | `handled_by` → `employee_id` | many → 1 |
| `mfg-daily-production` | `reference_id` → `production_id` (when `PRODUCTION`) | many → 1 |
| `sales-d2c-orders` | `reference_id` → `order_id` (when `DISPATCH`) | many → 1 |
| `proc-grn` / `sales-d2c-returns` / `inv-stock-count` (future) | `reference_id` | many → 1 |

## Growth & archival

- Highest-volume inventory sheet: roughly one IN per production/receipt + one OUT per order line. At ~1000 units/month, expect ~1,500–2,500 rows/month, ~25k/year.
- Sheets handles a year or two. Archive policy: at fiscal year-end, copy to `inv-stock-movement-archive-YYYY`, record each SKU's closing balance as the next year's opening, and clear from active.
