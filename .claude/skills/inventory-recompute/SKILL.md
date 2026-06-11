---
name: inventory-recompute
description: >-
  Event-sourced inventory engine for Company OS. Use this whenever the user wants to recompute, refresh,
  rebuild, or reconcile finished-goods stock, generate the stock-movement ledger, check stock levels, or
  see reorder alerts / low-stock / out-of-stock items. Triggers include "recompute inventory", "refresh
  stock", "what needs reordering", "stock movement ledger", "how many units of X do we have", "reconcile
  inventory", or any request to regenerate inv-finished-goods / inv-stock-movement from the source event
  logs. It READS the append-only trackers (inv-opening-balances, mfg-daily-production, sales-d2c-orders,
  plus manual movements) and REGENERATES the derived snapshot + ledger under reports/inventory/. It never
  hand-edits stock numbers; everything is recomputed from events.
---

# Inventory Recompute — event-sourced stock engine

You keep finished-goods stock honest by recomputing it from source events, never by hand-editing numbers.

## Core rule
```
qty_on_hand   = opening_qty + Σ(IN after cutover) − Σ(OUT after cutover)
qty_reserved  = open order lines (RESERVED / PACKED, not yet shipped)
qty_available = qty_on_hand − qty_reserved
```

## What it reads (inputs)
All under `trackers/` (resolved relative to the repo root):
- `inv-opening-balances` — per-SKU baseline at the cutover date.
- `mfg-daily-production` — `PACKING` completions become `PRODUCTION_IN`.
- `sales-d2c-orders` — `SHIPPED/DELIVERED/RETURNED` lines become `SALES_OUT`; `RESERVED/PACKED` lines become reservations.
- `reports/inventory/inputs/manual-movements.csv` — GRN receipts, returns, scrap, stock-count adjustments
  (stand-in for the future `proc-grn` / `sales-d2c-returns` / `inv-stock-count` trackers). A sample lives in
  `references/manual-movements.sample.csv`; copy it into `reports/inventory/inputs/` to use.

## What it writes (outputs — regenerated every run)
All under `reports/inventory/`:
- `stock-movement.csv` — the unified `inv-stock-movement` ledger (stable `STM-YYYY-NNNNN` ids).
- `finished-goods.csv` — the recomputed `inv-finished-goods` snapshot (on_hand, reserved, available, stock_status, value).
- `reorder-report.txt` — reorder alerts (available ≤ reorder point) + reconciliation vs the prior snapshot.

## Run
```bash
python3 .claude/skills/inventory-recompute/scripts/recompute_inventory.py [--root .]
```
Paths are resolved relative to the repo root (4 levels up from the script); pass `--root` to override. The
script reads only the trackers and writes only under `reports/inventory/` — safe to run any time, and
safe to schedule (e.g. a nightly stock refresh).

## How to handle a request
- **"Recompute / refresh inventory"** → run the script, then relay the headline: total active inventory
  value, count of low/out-of-stock SKUs, and any reconciliation drift.
- **"What needs reordering?"** → run it and read the REORDER ALERTS section of `reorder-report.txt`.
- **"How much of `<SKU>` do we have?"** → run it (or read the latest `finished-goods.csv`) and report
  on_hand / reserved / available for that SKU.
- Always **present** the generated `finished-goods.csv` or `reorder-report.txt` and give a short readout;
  don't paste the whole ledger into chat.

## Relationships
Feeds nothing back into the trackers (read-only). The recomputed snapshot is the truth that downstream
skills (e.g. the marketing daily report's stock nudge) reference for AQM-PRO-01 availability.
