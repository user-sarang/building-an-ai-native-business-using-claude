#!/usr/bin/env python3
"""Organize & reconcile the creative library against creatives-index.csv.

Usage:
    python organize_creatives.py [--root .] [--apply]

Dry run by default: reports unindexed files, missing-file (orphan) index rows, and naming violations.
With --apply it appends correctly-named, unindexed files to creatives-index.csv. It never renames,
deletes, or edits existing rows.
"""
import argparse, csv, os, re, sys
from pathlib import Path

PLATFORMS = {"meta", "google", "amazon", "instagram", "youtube"}
FORMATS = {"static", "video", "carousel", "story"}
FMT_ENUM = {"static": "STATIC", "video": "VIDEO", "carousel": "CAROUSEL", "story": "STORY"}
PLAT_ENUM = {"meta": "META", "google": "GOOGLE", "amazon": "AMAZON",
             "instagram": "INSTAGRAM", "youtube": "YOUTUBE"}
SKIP = {"readme.md", "creatives-index.csv", ".gitkeep", "_place_files_here.txt"}
NAME_RE = re.compile(r"^(?P<utm>.+?)__(?P<platform>[^_]+)__(?P<format>[^_]+)__(?P<concept>.+?)__v(?P<variant>[a-z0-9]+)\.(?P<ext>[A-Za-z0-9]+)$")

INDEX_HEADER = ["creative_id", "campaign_id", "utm_campaign", "file_path", "format",
                "platform", "headline", "concept", "variant", "created_date", "status", "notes"]


def load_campaigns(root: Path):
    p = root / "trackers/mkt-campaigns/sample-data.csv"
    by_utm = {}
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            by_utm[r["utm_campaign"]] = r["campaign_id"]
    return by_utm


def load_index(root: Path):
    p = root / "marketing/creatives/creatives-index.csv"
    rows = []
    if p.exists():
        with open(p, newline="") as f:
            rows = list(csv.DictReader(f))
    return p, rows


def next_creative_id(rows):
    mx = 0
    for r in rows:
        m = re.match(r"CRV-\d{4}-(\d+)", r["creative_id"])
        if m:
            mx = max(mx, int(m.group(1)))
    return mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    camps = load_campaigns(root)
    index_path, index_rows = load_index(root)
    indexed_paths = {r["file_path"] for r in index_rows}

    creatives_dir = root / "marketing/creatives"
    found, violations = [], []
    for dirpath, _dirs, files in os.walk(creatives_dir):
        folder = Path(dirpath).name
        if Path(dirpath) == creatives_dir:
            continue
        for fn in files:
            if fn.lower() in SKIP:
                continue
            rel = f"{folder}/{fn}"
            m = NAME_RE.match(fn)
            if not m:
                violations.append((rel, "filename does not match <utm>__<platform>__<format>__<concept>__v<variant>.<ext>"))
                continue
            g = m.groupdict()
            if g["utm"] != folder:
                violations.append((rel, f"utm '{g['utm']}' != folder '{folder}'"))
                continue
            if g["utm"] not in camps:
                violations.append((rel, f"utm '{g['utm']}' not found in mkt-campaigns"))
                continue
            if g["platform"] not in PLATFORMS:
                violations.append((rel, f"bad platform '{g['platform']}'"))
                continue
            if g["format"] not in FORMATS:
                violations.append((rel, f"bad format '{g['format']}'"))
                continue
            found.append((rel, g))

    found_paths = {rel for rel, _ in found}
    unindexed = [(rel, g) for rel, g in found if rel not in indexed_paths]
    orphans = [r["file_path"] for r in index_rows if r["file_path"] not in found_paths]

    print(f"== Creative library reconcile ({root.name}) ==")
    print(f"  assets on disk (valid names): {len(found)}")
    print(f"  rows in index:                {len(index_rows)}")
    print(f"  unindexed (new) files:        {len(unindexed)}")
    print(f"  orphan index rows (no file):  {len(orphans)}")
    print(f"  naming violations:            {len(violations)}")

    if unindexed:
        print("\n  NEW files not yet in index:")
        for rel, _ in unindexed:
            print(f"    + {rel}")
    if orphans:
        print("\n  ORPHAN index rows (file missing on disk):")
        for fp in orphans:
            print(f"    ? {fp}")
    if violations:
        print("\n  VIOLATIONS (fix the filename, then re-run):")
        for rel, why in violations:
            print(f"    ! {rel}  --  {why}")

    if unindexed and args.apply:
        n = next_creative_id(index_rows)
        added = []
        for rel, g in sorted(unindexed):
            n += 1
            added.append({
                "creative_id": f"CRV-2026-{n:04d}",
                "campaign_id": camps[g["utm"]],
                "utm_campaign": g["utm"],
                "file_path": rel,
                "format": FMT_ENUM[g["format"]],
                "platform": PLAT_ENUM[g["platform"]],
                "headline": "",
                "concept": g["concept"],
                "variant": g["variant"].upper(),
                "created_date": "",
                "status": "DRAFT",
                "notes": "auto-indexed by marketing-head",
            })
        with open(index_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=INDEX_HEADER)
            w.writeheader()
            w.writerows(index_rows + added)
        print(f"\n  APPLIED: added {len(added)} row(s) to creatives-index.csv (status=DRAFT).")
    elif unindexed:
        print("\n  (dry run) re-run with --apply to add the new files to the index.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
