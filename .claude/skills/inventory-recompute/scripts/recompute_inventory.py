#!/usr/bin/env python3
"""
recompute_inventory.py  —  the inventory recompute engine for Company OS.

Event-sourced design: you only ever APPEND events to the source logs.
This engine reads them all and REGENERATES the derived state from scratch:

  INPUTS  (append-only event logs + baseline)
    - inv-opening-balances      : per-SKU stock at the cutover date
    - mfg-daily-production       : PACKING completions  -> PRODUCTION_IN
    - sales-d2c-orders          : shipped/delivered/returned lines -> SALES_OUT
                                  reserved/packed lines           -> reservations
    - manual-movements.csv      : GRN receipts, returns, scrap, stock-count
                                  (stand-in for future proc-grn / sales-d2c-returns
                                   / inv-stock-count trackers)

  OUTPUTS (never hand-edited — rebuilt every run, under reports/inventory/)
    - stock-movement.csv        : the unified inv-stock-movement ledger
    - finished-goods.csv        : the recomputed inv-finished-goods snapshot
    - reorder-report.txt        : reorder alerts + reconciliation vs the prior snapshot

Rule:  qty_on_hand = opening_qty + Σ(IN after cutover) − Σ(OUT after cutover)
       qty_reserved = open order lines (RESERVED/PACKED, not yet shipped)
       qty_available = qty_on_hand − qty_reserved

Run:   python3 .claude/skills/inventory-recompute/scripts/recompute_inventory.py [--root .]
"""

import argparse, csv, os, sys
from datetime import date

# ---------- paths (uniform repo layout) ----------
# This script lives at <root>/.claude/skills/inventory-recompute/scripts/recompute_inventory.py
ap = argparse.ArgumentParser()
ap.add_argument("--root", default=None, help="repo root; defaults to 4 levels up from this script")
args, _ = ap.parse_known_args()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(args.root) if args.root else os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
TRACKERS = os.path.join(ROOT, "trackers")
OUT_DIR = os.path.join(ROOT, "reports", "inventory")
INPUT_DIR = os.path.join(OUT_DIR, "inputs")


def data_path(tracker):
    """Locate a tracker's seed/live data under trackers/<tracker>/sample-data.csv."""
    for p in (os.path.join(TRACKERS, tracker, "sample-data.csv"),
              os.path.join(ROOT, tracker, "sample-data.csv")):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"No data found for {tracker}")


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

# ---------- rules ----------
OUT_STATUSES      = {"SHIPPED", "DELIVERED", "RETURNED"}   # stock has physically left
RESERVED_STATUSES = {"RESERVED", "PACKED"}                 # committed, not yet shipped
DIRECTION = {
    "PRODUCTION_IN": "IN", "PURCHASE_IN": "IN", "SALES_RETURN_IN": "IN", "ADJUSTMENT_IN": "IN",
    "SALES_OUT": "OUT", "SCRAP_OUT": "OUT", "ADJUSTMENT_OUT": "OUT",
}
TYPE_ORDER = ["PRODUCTION_IN", "PURCHASE_IN", "SALES_RETURN_IN", "ADJUSTMENT_IN",
              "SALES_OUT", "SCRAP_OUT", "ADJUSTMENT_OUT"]
WAREHOUSE_OWNER = "EMP-012"   # default handler for dispatch movements

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- load baseline + attributes ----
    opening = {}
    for r in read_csv(data_path("inv-opening-balances")):
        opening[r["sku_id"]] = {
            "as_of": r["as_of_date"],
            "qty": int(r["opening_qty"]),
            "unit_cost": int(r["unit_cost"]) if r.get("unit_cost") else 0,
        }

    attrs = {}
    for r in read_csv(data_path("inv-finished-goods")):
        attrs[r["sku_id"]] = r
    def cost_of(sku):
        if sku in opening and opening[sku]["unit_cost"]:
            return opening[sku]["unit_cost"]
        return int(attrs.get(sku, {}).get("unit_cost", 0) or 0)
    def name_of(sku):
        return attrs.get(sku, {}).get("product_name", sku)

    movements = []  # dict rows, ids assigned after sorting

    # ---- 1. PRODUCTION_IN  <- mfg-daily-production PACKING completions ----
    for r in read_csv(data_path("mfg-daily-production")):
        if r["station"] != "PACKING":
            continue
        qty = int(r["units_completed"])
        if qty <= 0:
            continue
        movements.append(dict(
            movement_date=r["date"], movement_type="PRODUCTION_IN",
            sku_id=r["product_sku"], quantity=qty,
            reference_type="PRODUCTION", reference_id=r["production_id"],
            handled_by=r["operator_id"], unit_cost=cost_of(r["product_sku"]),
            notes="",
        ))

    # ---- 2. SALES_OUT + reservations  <- sales-d2c-orders ----
    reserved = {}
    for r in read_csv(data_path("sales-d2c-orders")):
        status = r["fulfillment_status"]
        sku, qty = r["sku_id"], int(r["quantity"])
        if status in OUT_STATUSES:
            movements.append(dict(
                movement_date=r["order_date"], movement_type="SALES_OUT",
                sku_id=sku, quantity=qty,
                reference_type="DISPATCH", reference_id=r["order_id"],
                handled_by=WAREHOUSE_OWNER, unit_cost=cost_of(sku),
                notes="",
            ))
        if status in RESERVED_STATUSES:
            reserved[sku] = reserved.get(sku, 0) + qty

    # ---- 3. manual movements (GRN / returns / scrap / counts) ----
    man_path = os.path.join(INPUT_DIR, "manual-movements.csv")
    if os.path.exists(man_path):
        for r in read_csv(man_path):
            movements.append(dict(
                movement_date=r["movement_date"], movement_type=r["movement_type"],
                sku_id=r["sku_id"], quantity=int(r["quantity"]),
                reference_type=r["reference_type"], reference_id=r.get("reference_id", ""),
                handled_by=r["handled_by"],
                unit_cost=int(r["unit_cost"]) if r.get("unit_cost") else cost_of(r["sku_id"]),
                notes=r.get("notes", ""),
            ))

    # ---- assign direction, sort, assign stable ids ----
    for m in movements:
        m["direction"] = DIRECTION[m["movement_type"]]
    movements.sort(key=lambda m: (m["movement_date"],
                                  TYPE_ORDER.index(m["movement_type"]),
                                  m["sku_id"]))
    yr = movements[0]["movement_date"][:4] if movements else str(date.today().year)
    for i, m in enumerate(movements, 1):
        m["movement_id"] = f"STM-{yr}-{i:05d}"

    # ---- recompute snapshot:  on_hand = opening + IN - OUT (after cutover) ----
    skus = set(opening) | set(attrs) | {m["sku_id"] for m in movements}
    on_hand, last_move = {}, {}
    for s in skus:
        on_hand[s] = opening.get(s, {}).get("qty", 0)
    for m in movements:
        s, q = m["sku_id"], m["quantity"]
        cutover = opening.get(s, {}).get("as_of", "0000-00-00")
        if m["movement_date"] > cutover:
            on_hand[s] += q if m["direction"] == "IN" else -q
        if m["movement_date"] > last_move.get(s, ""):
            last_move[s] = m["movement_date"]

    # ---- write the unified ledger ----
    mv_cols = ["movement_id","movement_date","movement_type","direction","sku_id",
               "product_name","quantity","reference_type","reference_id","handled_by",
               "unit_cost","notes"]
    with open(os.path.join(OUT_DIR, "stock-movement.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=mv_cols); w.writeheader()
        for m in movements:
            w.writerow({**m, "product_name": name_of(m["sku_id"])})

    # ---- write the recomputed snapshot ----
    fg_cols = ["sku_id","product_name","category","sourcing","uom","qty_on_hand",
               "qty_reserved","qty_available","reorder_point","reorder_qty","unit_cost",
               "stock_value","warehouse_location","stock_status","last_movement_date","is_active"]
    alerts, total_value = [], 0
    snap_rows = []
    for s in sorted(skus):
        a = attrs.get(s, {})
        oh = on_hand[s]
        res = reserved.get(s, 0)
        av = oh - res
        rop = int(a.get("reorder_point", 0) or 0)
        is_active = a.get("is_active", "TRUE")
        uc = cost_of(s)
        sv = oh * uc
        if is_active == "FALSE":
            status = "DISCONTINUED"
        elif av <= 0:
            status = "OUT_OF_STOCK"
        elif av <= rop:
            status = "LOW_STOCK"
        else:
            status = "IN_STOCK"
        if is_active != "FALSE":
            total_value += sv
            if status in ("LOW_STOCK", "OUT_OF_STOCK"):
                alerts.append((s, name_of(s), av, rop, int(a.get("reorder_qty",0) or 0), status))
        snap_rows.append(dict(
            sku_id=s, product_name=name_of(s), category=a.get("category",""),
            sourcing=a.get("sourcing",""), uom=a.get("uom","PCS"),
            qty_on_hand=oh, qty_reserved=res, qty_available=av,
            reorder_point=rop, reorder_qty=a.get("reorder_qty",""),
            unit_cost=uc, stock_value=sv,
            warehouse_location=a.get("warehouse_location",""),
            stock_status=status, last_movement_date=last_move.get(s,""),
            is_active=is_active,
        ))
    with open(os.path.join(OUT_DIR, "finished-goods.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fg_cols); w.writeheader()
        w.writerows(snap_rows)

    # ---- reconciliation vs the prior (hand-kept) snapshot ----
    drift = []
    for s in sorted(skus):
        prior = attrs.get(s, {}).get("qty_on_hand")
        if prior is not None and int(prior) != on_hand[s]:
            drift.append((s, int(prior), on_hand[s]))

    # ---- report ----
    lines = []
    lines.append("INVENTORY RECOMPUTE REPORT")
    lines.append(f"Generated: {date.today()}   Movements processed: {len(movements)}   SKUs: {len(skus)}")
    lines.append("")
    lines.append(f"Total active inventory value: Rs {total_value:,}")
    lines.append("")
    lines.append("REORDER ALERTS (available <= reorder point):")
    if alerts:
        for s, n, av, rop, rq, st in alerts:
            lines.append(f"  [{st:12}] {s:14} {n:28} avail {av:>4} (reorder pt {rop}, suggest order {rq})")
    else:
        lines.append("  none")
    lines.append("")
    lines.append("RECONCILIATION vs prior snapshot (engine replaces stale hand-typed numbers):")
    if drift:
        for s, prior, now in drift:
            lines.append(f"  {s:14} prior {prior:>5}  ->  computed {now:>5}   (delta {now-prior:+d})")
    else:
        lines.append("  no drift — prior snapshot matched computed values")
    report = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "reorder-report.txt"), "w") as f:
        f.write(report + "\n")
    print(report)
    print(f"\nWrote: {OUT_DIR}/stock-movement.csv, finished-goods.csv, reorder-report.txt")

if __name__ == "__main__":
    main()
