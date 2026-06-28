"""Reviewer: forensic brand+quality audit of a generated creative via Gemini vision.

Runs the strict checklist, prints a per-criterion verdict, appends one row per
image to an audit CSV, and exits 0 only if the image PASSES every blocking
criterion (so callers can gate acceptance on the exit code).

Usage:
  python audit_image.py --image candidates/v1.png --csv audit/audit.csv \
      --brief brief.md [--brand-profile inputs/your_brand/brand-profile.md] \
      [--run-id 2026-06-28_diwali] [--round 1]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import mimetypes
import re
import sys
from pathlib import Path

from gemini_client import audit_model, get_client

# Blocking criteria — ALL must PASS for the image to be accepted.
CRITERIA = [
    ("purple_dominant", "Samalyal purple is visibly the dominant color."),
    ("no_price_slab", "No screaming price slab / slashed-price discount styling."),
    ("illustration_style", "Hand-made / illustrated look, NOT photoreal stock food."),
    ("warm_homely_tone", "Warm, homely, mom-and-pop emotional feeling."),
    ("on_brand_typography", "Typography is cozy/friendly and on-brand, not loud slabs."),
    ("logo_correct", "Logo (if present) undistorted with clear space; NA if absent."),
    ("text_legible_spelling", "All text is legible and correctly spelled."),
    ("composition_safe_margins", "Composition fits the format; key elements within safe margins."),
    ("no_artifacts_anatomy", "No visual artifacts, warping, or broken anatomy."),
    ("claims_compliance", "No false/unsupported claims; required disclaimers present."),
    ("competitor_differentiation", "Clearly distinct from competitor (Swiggy/Big Bowl) styling."),
    ("resolution_aspect", "Resolution/aspect ratio correct for the intended placement."),
]

CSV_COLUMNS = (
    ["run_id", "timestamp", "image_file", "model", "round"]
    + [k for k, _ in CRITERIA]
    + ["overall_verdict", "blocking_failures", "summary"]
)


def _image_part(path: Path):
    from google.genai import types

    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)


def _build_prompt(brief: str, brand_profile: str) -> str:
    lines = "\n".join(f'- "{k}": {desc}' for k, desc in CRITERIA)
    return f"""You are a forensic brand & quality reviewer for the Samalyal brand.
Audit the attached marketing image AGAINST the brand profile and the brief.
Be strict and literal. When unsure, FAIL.

=== BRAND PROFILE ===
{brand_profile}

=== BRIEF FOR THIS CREATIVE ===
{brief}

=== CHECKLIST (evaluate every item) ===
{lines}

For each criterion return: "pass" (meets the bar), "fail" (does not), or "na"
(not applicable, e.g. no logo present). Add a one-sentence evidence note citing
what you SEE in the image.

Return ONLY valid JSON, no markdown fences, in exactly this shape:
{{
  "criteria": {{
    "purple_dominant": {{"verdict": "pass|fail|na", "note": "..."}},
    ... one entry for every criterion key above ...
  }},
  "summary": "2-3 sentence overall forensic assessment."
}}"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--brief", required=True, help="brief file (md/txt)")
    ap.add_argument("--brand-profile", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--round", default="1")
    args = ap.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"ERROR: image not found: {img_path}", file=sys.stderr)
        return 2

    brief = Path(args.brief).read_text(encoding="utf-8") if Path(args.brief).exists() else args.brief
    brand_profile = (
        Path(args.brand_profile).read_text(encoding="utf-8")
        if args.brand_profile and Path(args.brand_profile).exists()
        else "(brand profile not supplied)"
    )

    client = get_client()
    model = audit_model()
    print(f"Auditing {img_path.name} with {model}...", file=sys.stderr)
    resp = client.models.generate_content(
        model=model,
        contents=[_build_prompt(brief, brand_profile), _image_part(img_path)],
    )

    try:
        data = _parse_json(resp.text or "")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not parse audit JSON: {exc}", file=sys.stderr)
        print(resp.text or "<empty>", file=sys.stderr)
        return 2

    crit = data.get("criteria", {})
    failures = []
    row = {
        "run_id": args.run_id,
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "image_file": str(img_path),
        "model": model,
        "round": args.round,
        "summary": data.get("summary", "").replace("\n", " ").strip(),
    }
    for key, _ in CRITERIA:
        verdict = str(crit.get(key, {}).get("verdict", "fail")).lower()
        if verdict not in ("pass", "fail", "na"):
            verdict = "fail"
        row[key] = verdict
        if verdict == "fail":
            failures.append(key)

    overall = "PASS" if not failures else "FAIL"
    row["overall_verdict"] = overall
    row["blocking_failures"] = ";".join(failures)

    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)

    # Human-readable console report
    print(f"\n=== AUDIT: {img_path.name}  ->  {overall} ===")
    for key, desc in CRITERIA:
        v = row[key].upper()
        note = crit.get(key, {}).get("note", "")
        mark = {"PASS": "OK ", "FAIL": "XX ", "NA": "-- "}.get(v, "?? ")
        print(f"  [{mark}] {key}: {note}")
    print(f"Summary: {row['summary']}")
    print(f"CSV row appended -> {csv_path}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
