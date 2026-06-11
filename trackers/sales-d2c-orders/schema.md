# `sales-d2c-orders` — schema

Every direct-to-consumer order, captured **one row per order line** (per SKU within an order). This is the daily demand feed from your online channels — Shopify (your own store) and Amazon — and the trigger that reserves and then draws down `inv-finished-goods`.

**Category**: Sales (`sales-*`, header color Purple `#A855F7`)
**Tier**: T1 (foundational, week 1)
**Type**: Transaction sheet (append-only)
**Owner**: D2C Lead (`EMP-014`, Divya)
**Daily effort**: ~10 minutes — import/paste the day's orders from each channel
**Scope**: The order itself. **Returns** live in `sales-d2c-returns` and **coupon definitions** in `sales-d2c-coupons` — this sheet only references a coupon code and logs the discount actually applied.

## Grain: one row per order line

An order with three different products is three rows that share one `order_id`. This keeps per-SKU analysis and inventory reservations clean (each line points at exactly one SKU). Order-level totals are the sum of an order's lines, which Claude computes on the fly.

By convention, an **order-level charge** (shipping) is recorded on the **first line** of the order and left `0` on the rest, so summing a column across the order never double-counts.

## Tab structure

For v1: **one tab**, `data`. A `dashboard` tab (today's orders, revenue, AOV, channel split, top SKUs) can be added later per Design Bible §D.3.

## Columns (23)

| Col | Header | Type | Required | Notes |
|---|---|---|---|---|
| A | `order_line_id` | Text | yes | Primary key. Format `DOL-YYYY-NNNNN`, e.g. `DOL-2026-00001`. Immutable. Monospace. |
| B | `order_id` | Text | yes | Groups lines of one order. Format `ORD-YYYY-NNNN`. |
| C | `order_date` | Date | yes | `YYYY-MM-DD` — date the order was placed |
| D | `channel` | Enum (dropdown) | yes | See enum below |
| E | `channel_order_ref` | Text | yes | The channel's own order number (e.g. Amazon `402-…`), for reconciliation |
| F | `customer_id` | Text (FK → `cust-master`) | yes | `CUST-NNNNN`. Master is future; ID reserved now. |
| G | `customer_name` | Text | yes | Denormalized readable name |
| H | `customer_city` | Text | no | Ship-to city |
| I | `customer_state` | Text | no | Ship-to state — GST place-of-supply |
| J | `sku_id` | Text (FK → `inv-finished-goods`) | yes | Product ordered, e.g. `AQM-PRO-01` |
| K | `product_name` | Text | yes | Denormalized readable name |
| L | `quantity` | Number | yes | Units of this SKU in this line (≥ 1) |
| M | `unit_price` | Number (INR) | yes | Selling price per unit, **exclusive of GST** (taxable value) |
| N | `line_amount` | Number (INR) | yes | `quantity × unit_price` (gross, before discount). Sanity-checked. |
| O | `discount_amount` | Number (INR) | no | Discount applied to this line (≥ 0; 0 if none) |
| P | `coupon_code` | Text (FK → `sales-d2c-coupons`) | no | Code used, if any. Full coupon detail lives in the coupons tracker. |
| Q | `shipping_charge` | Number (INR) | no | Shipping billed to customer. Recorded on the order's first line only. |
| R | `tax_amount` | Number (INR) | yes | GST on this line = 18% of `(line_amount − discount_amount)`. Sanity-checked. |
| S | `net_amount` | Number (INR) | yes | What the customer pays for this line = `line_amount − discount_amount + shipping_charge + tax_amount`. Sanity-checked. |
| T | `payment_method` | Enum (dropdown) | yes | `PREPAID` / `COD` |
| U | `payment_status` | Enum (dropdown) | yes | See enum below |
| V | `fulfillment_status` | Enum (dropdown) | yes | See enum below — this is the field that drives inventory |
| W | `notes` | Text | no | Free text — backorder reason, address issue, etc. |

## Enums

### `channel` (column D)
| Value | Meaning |
|---|---|
| `SHOPIFY` | Your own D2C store |
| `AMAZON` | Amazon India marketplace |

*(Extend with new marketplaces as you add them, e.g. `FLIPKART`.)*

### `payment_method` (column T)
`PREPAID` · `COD`

### `payment_status` (column U)
| Value | Meaning |
|---|---|
| `PAID` | Money received (prepaid captured) |
| `COD_TO_COLLECT` | Cash to be collected on delivery |
| `PENDING` | Awaiting payment / authorization |
| `REFUNDED` | Money returned (cancellation or return) |

### `fulfillment_status` (column V) — the inventory hook

| Value | Meaning | Inventory effect |
|---|---|---|
| `PENDING` | New, not yet processed | none |
| `RESERVED` | Confirmed; stock earmarked | **+** `qty_reserved` in `inv-finished-goods` |
| `PACKED` | Picked & boxed, awaiting pickup | still reserved |
| `SHIPPED` | Handed to courier | **−** `qty_on_hand` and **−** `qty_reserved` |
| `DELIVERED` | Received by customer | (already shipped) |
| `CANCELLED` | Killed before shipping | release any reservation |
| `RETURNED` | Came back after delivery | handled in `sales-d2c-returns` → inbound movement |

> This is exactly the reserve-then-deduct flow: `RESERVED` parks the stock, `SHIPPED` actually removes it. Each status change posts a row in `inv-stock-movement`, which is what keeps the `inv-finished-goods` snapshot honest.

## Validation rules to set

1. Column A (`order_line_id`): protected; unique.
2. Columns D, T, U, V (enums): Data Validation → Dropdown (chip style).
3. Columns C (`order_date`): Date validation.
4. Columns L–S (quantities & money): Number → ≥ 0; `L` (`quantity`) ≥ 1; money columns currency-formatted `₹ #,##,##0`.
5. Reconciliation (flag on read, don't hard-block):
   - `line_amount = quantity × unit_price`
   - `tax_amount = round(0.18 × (line_amount − discount_amount))`
   - `net_amount = line_amount − discount_amount + shipping_charge + tax_amount`

## What's NOT stored (Claude computes on the fly)

- **Order total / AOV** — sum `net_amount` per `order_id`; average across orders.
- **Daily & monthly revenue** — sum `net_amount` (optionally excluding `CANCELLED`/`RETURNED`).
- **Channel split** — group by `channel`.
- **Best-sellers** — sum `quantity` by `sku_id`.
- **Units to reserve/ship today** — filter by `fulfillment_status`, join to `inv-finished-goods` for stock availability.
- **GST output liability** — sum `tax_amount` for the period (feeds `fin-gst-output`).

## Natural key

`order_line_id` is the primary key. `(order_id, sku_id)` is unique within an order.

## Audit / change history

Rely on **Google Sheets version history** (orders are imported daily and rarely hand-edited; `channel_order_ref` is the external reconciliation key). Add Design Bible §A.4 audit columns later if orders get edited in-place frequently.

## Relationships

| Tracker | References via | Cardinality |
|---|---|---|
| `cust-master` (future) | `customer_id` | many → 1 |
| `inv-finished-goods` | `sku_id`; `fulfillment_status` drives reserve/deduct | many → 1 / feeds |
| `inv-stock-movement` | each status change posts a movement | feeds |
| `sales-d2c-returns` | returns reference `order_id` / `order_line_id` | 1 → many |
| `sales-d2c-coupons` | `coupon_code` | many → 1 |
| `fin-gst-output` | `tax_amount` rolls up to the GST register | feeds |

## Growth & archival

- ~1000 units/month, many multi-unit orders → roughly 600–900 orders/month, ~700–1,100 lines/month; ~10k–13k rows/year.
- Sheets handles a year or two comfortably. Archive policy: at fiscal year-end, copy to `sales-d2c-orders-archive-YYYY` and clear from active.
