# Forensic Audit Checklist (strict brand + quality gate)

The reviewer agent evaluates every generated image against ALL of the following.
**Every criterion must be `pass` (or `na` where genuinely inapplicable) for the
image to be accepted.** A single `fail` blocks acceptance and the image is sent
back to the creator with the failing notes.

Keys here match the column keys in `audit.csv` and in `scripts/audit_image.py`.

## Brand criteria

1. **purple_dominant** — Samalyal purple (`#6B3FA0` family) is visibly the
   dominant color of the creative.
2. **no_price_slab** — No screaming price slab, slashed prices, or discount-shout
   styling (that is the competitor lane).
3. **illustration_style** — Hand-made / illustrated / painterly look. NOT
   photoreal stock food photography.
4. **warm_homely_tone** — Communicates warm, homely, mom-and-pop, home-cooked care.
5. **on_brand_typography** — Cozy, friendly, legible type. No aggressive italic
   price slabs or neon delivery-app styling.
6. **logo_correct** — If a logo appears, it is undistorted with adequate clear
   space and correct color. `na` if no logo is present.
7. **competitor_differentiation** — Clearly distinct from competitor (Swiggy /
   Big Bowl) creatives. If it could be mistaken for one, it FAILS.

## Quality criteria

8. **text_legible_spelling** — All text is sharp, readable, and correctly spelled
   (Gemini image models can garble text — check letter by letter).
9. **composition_safe_margins** — Key elements sit within safe margins for the
   intended placement; nothing important is cropped.
10. **no_artifacts_anatomy** — No visual artifacts, warping, melted edges, extra
    fingers, or broken anatomy.
11. **claims_compliance** — No false or unsupported claims; any legally required
    disclaimer is present and legible.
12. **resolution_aspect** — Resolution and aspect ratio match the intended
    placement (e.g. 9:16 for stories/reels).

## Verdict rule

```
overall = PASS  iff  every criterion in {pass, na}  (no fails)
overall = FAIL  iff  any criterion == fail
```

On `FAIL`, collect the failing criteria + notes and feed them back to the creator
for the next round. Default retry budget: **3 rounds**, then surface to the user.
