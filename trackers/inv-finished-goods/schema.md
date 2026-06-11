# `inv-finished-goods` — schema

The **live stock snapshot** of every sellable finished product — both the AQI monitors you build and the white-label speakers you resell. One row per SKU, always current. This is the tracker that answers "can I fulfil today's orders, and what's about to run out?"

**Category**: Inventory (`inv-*`, header color Amber `#EAB308`)
**Tier**: T1 (foundational, week 1)
**Type**: Master sheet (in-place edits; soft delete via `is_active`, never hard delete)
**Owner**: Warehouse & Dispatch (`EMP-012`, Ananya), reviewed by Procurement (`EMP-011`, Suresh)
**Edit frequency**: Updated as stock moves — but the *row set* changes only when a SKU is added/retired.

## Design decision: snapshot vs. ledger

This sheet holds **current balances only** (on-hand, reserved, available). Every individual movement — production in, dispatch out, return in, adjustment — is logged append-only in the separate **`inv-stock-movement`** tracker (per `03-sources-of-truth.md`). That keeps this sheet a clean, fast "what do I have right now" view, while full history stays auditable next door.

- `mfg-daily-production` PACKING completions → **increase** `qty_on_hand` (manufactured SKUs).
- `inv-dispatch` shipments → **decrease** `qty_on_hand`.
- `inv-returns` → **increase** `qty_on_hand` (or quarantine).
- Speakers/accessories enter via `proc-grn` (goods received), not production.

## Tab structure

For v1: **one tab**, `data`. A `dashboard` tab (KPI cards: total stock value, # SKUs below reorder, out-of-stock count) can be added later per Design Bible §D.3.

## Columns (16)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `sku_id` | Text | yes | Primary key. SKU code, e.g. `AQM-PRO-01`, `SPK-BT-05`. Immutable. Monospace. |
| B | `product_name` | Text | yes | Readable name, e.g. "AirSense Pro" |
| C | `category` | Enum (dropdown) | yes | See enum below |
| D | `sourcing` | Enum (dropdown) | yes | `MANUFACTURED` (built in-house) / `TRADED` (white-label, bought to resell) |
| E | `uom` | Enum (dropdown) | yes | Unit of measure — `PCS` / `BOX` / `SET` |
| F | `qty_on_hand` | Number | yes | Physical units in the warehouse right now (≥ 0) |
| G | `qty_reserved` | Number | yes | Allocated to confirmed-but-unshipped orders (≥ 0) |
| H | `qty_available` | Number | yes | Should equal `qty_on_hand − qty_reserved`. Sanity-checked on read. |
| I | `reorder_point` | Number | yes | Stock level at or below which you reorder/build more |
| J | `reorder_qty` | Number | no | Standard replenishment batch size |
| K | `unit_cost` | Number (INR) | yes | Landed cost (traded) or production cost (manufactured), per unit |
| L | `stock_value` | Number (INR) | yes | Should equal `qty_on_hand × unit_cost`. Sanity-checked on read. |
| M | `warehouse_location` | Text | no | Bin/rack, e.g. "A-03" |
| N | `stock_status` | Enum (dropdown) | yes | Status pill. See enum below |
| O | `last_movement_date` | Date | no | Date of most recent in/out (from `inv-stock-movement`). `YYYY-MM-DD` |
| P | `is_active` | Boolean | yes | `TRUE` / `FALSE`. Soft delete — retired SKUs stay with `FALSE`. |

## Enums

### `category` (column C)

| Value | Meaning |
|---|---|
| `AQI_MONITOR` | Finished air-quality monitor (your core product) |
| `SPEAKER` | White-label Bluetooth speaker / soundbar (resold) |
| `ACCESSORY` | Replacement sensors, adapters, mounts, filters |

### `sourcing` (column D)

| Value | Meaning |
|---|---|
| `MANUFACTURED` | Built in-house; replenished via `mfg-daily-production` |
| `TRADED` | Bought finished from a vendor; replenished via `proc-purchase-orders` → `proc-grn` |

### `stock_status` (column N) — drives the status-pill conditional formatting (Design Bible §D.2)

| Value | Meaning | Rule of thumb |
|---|---|---|
| `IN_STOCK` | Healthy | `qty_available > reorder_point` |
| `LOW_STOCK` | Reorder soon | `0 < qty_available ≤ reorder_point` |
| `OUT_OF_STOCK` | Cannot fulfil | `qty_available = 0` |
| `DISCONTINUED` | No longer sold | paired with `is_active = FALSE` |

> `stock_status` is stored (so the pill renders) but Claude validates it against the rule of thumb on read and flags mismatches.

## Validation rules to set

1. Column A (`sku_id`): protected; only Warehouse/Procurement edit. Unique.
2. Columns C, D, E, N (`category`, `sourcing`, `uom`, `stock_status`): Data Validation → Dropdown (chip style).
3. Columns F, G, H, I, J (quantities): Data Validation → Number → ≥ 0.
4. Columns K, L (`unit_cost`, `stock_value`): Number → ≥ 0; currency format `₹ #,##,##0` (Indian grouping).
5. `qty_available` (H) reconciles to `qty_on_hand − qty_reserved`; `stock_value` (L) to `qty_on_hand × unit_cost`. Flag on read, don't hard-block.
6. Column P (`is_active`): Dropdown `TRUE` / `FALSE`.

## What's NOT stored (Claude computes on the fly)

- **Days of cover** — `qty_available ÷ average daily dispatch` (joins to `inv-dispatch`).
- **SKUs below reorder point** — filter `qty_available ≤ reorder_point`.
- **Total finished-goods inventory value** — `SUM(stock_value)` for `is_active = TRUE`.
- **Fulfilment risk** — open order qty (from `sales-d2c-orders` / `sales-b2b-pipeline`) vs `qty_available`.
- **Dead stock** — SKUs with old `last_movement_date` and high `stock_value`.

## Natural key

`sku_id` is the primary key (this is a master sheet — one row per SKU, never appended per movement).

## Privacy & access

Contains cost/margin data (`unit_cost`, `stock_value`). Restrict view to founder, COO, finance, procurement, and warehouse owner. Not sensitive PII, but commercially confidential.

## Relationships

| Tracker | References / feeds | Cardinality |
|---|---|---|
| `cat-sku-master` (future) | `sku_id` → catalog master | 1 → 1 |
| `inv-stock-movement` | every in/out logged there, balances roll up here | 1 → many |
| `mfg-daily-production` | PACKING completions increment manufactured SKUs | feeds |
| `inv-dispatch` / `inv-returns` | decrement / increment on hand | feeds |
| `proc-grn` | traded-goods receipts increment on hand | feeds |

## Growth & archival

- ~10s of SKUs today, growing slowly. Stays tiny — a master sheet, not a log.
- Retired products: set `is_active = FALSE`, `stock_status = DISCONTINUED`. Never delete — keeps historical valuation and reporting intact.
