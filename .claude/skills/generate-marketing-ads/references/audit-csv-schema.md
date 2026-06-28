# Audit CSV Schema

One file per run: `marketing-ads/outputs/<run>/audit/audit.csv`.
One **row per image audited** (every candidate, every round — full forensic trail).

## Columns

| Column | Meaning |
|--------|---------|
| `run_id` | Run identifier (e.g. `2026-06-28_diwali-launch`) |
| `timestamp` | ISO timestamp of the audit |
| `image_file` | Path to the audited candidate |
| `model` | Gemini model used for the audit |
| `round` | Generation round (1, 2, 3…) |
| `purple_dominant` | pass / fail / na |
| `no_price_slab` | pass / fail / na |
| `illustration_style` | pass / fail / na |
| `warm_homely_tone` | pass / fail / na |
| `on_brand_typography` | pass / fail / na |
| `logo_correct` | pass / fail / na |
| `text_legible_spelling` | pass / fail / na |
| `composition_safe_margins` | pass / fail / na |
| `no_artifacts_anatomy` | pass / fail / na |
| `claims_compliance` | pass / fail / na |
| `competitor_differentiation` | pass / fail / na |
| `resolution_aspect` | pass / fail / na |
| `overall_verdict` | `PASS` (all pass/na) or `FAIL` (any fail) |
| `blocking_failures` | `;`-joined keys of failing criteria |
| `summary` | 2–3 sentence forensic assessment |

The column order and keys are produced by `scripts/audit_image.py` (`CSV_COLUMNS`)
and must stay in sync with `references/audit-checklist.md`.
