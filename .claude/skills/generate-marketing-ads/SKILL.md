---
name: generate-marketing-ads
description: "Generates on-brand marketing ad creatives (illustrations) using the Gemini image API, with a two-agent create-then-audit workflow. Use this skill whenever the user wants to create a marketing ad, ad creative, social/Instagram/story creative, brand illustration, campaign visual, or promo image for their brand. The skill reads brand and competitor references, ALWAYS asks clarifying questions and shows a preview/brief for approval before generating, then spawns a creator agent (brand illustrator) and a reviewer agent (forensic brand+quality auditor) that writes a per-image audit CSV; only audit-passed images are accepted. Triggers on: 'make an ad', 'create a creative', 'generate a marketing image', 'design a promo', 'new campaign visual'."
---

# Generate Marketing Ads

Creates beautiful, on-brand illustrated ad creatives through a disciplined
**create → forensic audit → accept-on-pass** loop driven by two agents.

## Layout this skill depends on

```
secrets/.env                          GEMINI_API_KEY, GEMINI_IMAGE_MODEL, GEMINI_AUDIT_MODEL
marketing-ads/inputs/competitor/      competitor refs (differentiate from)
marketing-ads/inputs/your_brand/      brand-profile.md (the bible) + logo.png
marketing-ads/inputs/ugc/             authenticity refs
marketing-ads/outputs/<run>/          per-run output (gitignored)
  ├── brief.md      approved brief
  ├── prompts/      one prompt file per variation (v1.txt, v2.txt, …)
  ├── run.sh        reproducible create→audit→accept command (gitignored with outputs)
  ├── candidates/   every generated attempt
  ├── accepted/     ONLY audit-passed finals
  └── audit/audit.csv   forensic audit, one row per image
.claude/skills/generate-marketing-ads/scripts/   gen_image.py, audit_image.py, gemini_client.py
.claude/skills/generate-marketing-ads/references/ checklist + agent specs + csv schema
```

## Setup (first run only)

1. Ensure `secrets/.env` exists with `GEMINI_API_KEY` (copy `secrets/.env.example`).
2. Install deps: `pip install -r .claude/skills/generate-marketing-ads/scripts/requirements.txt --break-system-packages`
3. Ensure `marketing-ads/inputs/your_brand/brand-profile.md` and (ideally) `logo.png` exist.

## Workflow — follow in order

### 1. Ground in the brand
Read `marketing-ads/inputs/your_brand/brand-profile.md`, skim
`marketing-ads/inputs/competitor/` and `marketing-ads/inputs/ugc/`. These define
what on-brand and differentiated mean.

### 2. ALWAYS ask clarifying questions (do not skip)
Use the question tool to confirm at minimum:
- **Objective** (launch, festival/Diwali, new dish, awareness, retarget…).
- **Placement & format** (IG story/reel 9:16, post 4:5/1:1, banner) and dimensions.
- **Core message / headline** and **CTA** (if any).
- **Hero subject** (which dish / scene / mood).
- **Number of variations** to produce.
- Any must-have or must-avoid elements, disclaimers, or copy.

### 3. Build and show a PREVIEW/brief, then WAIT for approval
Write `marketing-ads/outputs/<run>/brief.md` summarizing the above plus the
intended visual direction (style, palette, composition). Present this preview to
the user in plain language. **Do not generate any image until the user approves.**
Use a run id like `YYYY-MM-DD_<slug>`.

### 4. Write the prompts and a committed `run.sh` (ALWAYS)
After approval, write one prompt file per variation to
`marketing-ads/outputs/<run>/prompts/v1.txt`, `v2.txt`, … (full creative prompt
built from `brand-profile.md` + the brief + competitor differentiation/layout).

Then **always** generate `marketing-ads/outputs/<run>/run.sh` from
`references/run-template.sh`, filling in: the run id/path, the list of variations,
each variation's competitor layout reference (if used), the logo ref, and the
aspect ratio. This makes every campaign a single, reproducible command. Note:
`run.sh` lives under `outputs/` and is **gitignored** along with all other outputs
— it is for local reproducibility, not for committing. Keep `run.sh`
syntax-portable (works on macOS bash 3.2 — see template).

`run.sh` IS the create→audit→accept loop: for each variation it calls
`scripts/gen_image.py` then `scripts/audit_image.py`, copying only PASS images to
`accepted/`. Running the loop = running `run.sh` (or spawning the agents below to
do the same calls).

### 5. Creator — generate candidates
Either run `run.sh`, or spawn the creator agent (`references/creator-agent.md`).
Candidates land in `candidates/`; logo and any competitor **layout** refs are
passed via `--ref`, with the right `--aspect`.

### 6. Reviewer — forensic audit (independent)
For each candidate, `scripts/audit_image.py` (driven by `run.sh` or the reviewer
agent, `references/reviewer-agent.md` + `references/audit-checklist.md`) evaluates
all 12 criteria, appends a row to `audit/audit.csv`, and exits 0 only on PASS.

### 7. Accept only on PASS
Copy each PASS image to `accepted/`. For any FAIL, feed the failing criteria +
notes back to the creator and regenerate. **Retry budget: 3 rounds.** If still
failing, stop and surface the audit CSV + reasons instead of accepting.

### 8. Deliver
Present the accepted images and `audit/audit.csv`. Summarize which passed and any
notable audit findings.

## Running the agents

Spawn the creator and reviewer with the Task/Agent tool as **separate** agents so
the audit is genuinely independent of creation. Keep the creator out of the
accept/reject decision — only the reviewer's CSV verdict (script exit code) gates
acceptance.

## Hard rules

- Never generate before the user approves the brief.
- Never accept an image with any `fail` in the audit.
- Never commit `secrets/.env` or `marketing-ads/outputs/` (already gitignored).
- If a Samalyal creative could be mistaken for a Swiggy/Big Bowl ad, it has failed.
