#!/usr/bin/env bash
# TEMPLATE — the skill copies this to marketing-ads/outputs/<run>/run.sh and fills in:
#   - RUN  (the run path)
#   - the variation list  (v1 v2 v3 …)
#   - each variation's competitor LAYOUT reference in the case block (or remove it)
#   - --aspect for the primary format
# Portable for macOS bash 3.2 (note the ${REF[@]+"${REF[@]}"} guard under set -u).
#
# Usage, from the repo root (company_os/):
#   bash marketing-ads/outputs/<run>/run.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO"

RUN="marketing-ads/outputs/<RUN_ID>"           # <-- fill in
SK=".claude/skills/generate-marketing-ads/scripts"
BRAND="marketing-ads/inputs/your_brand/brand-profile.md"
LOGO="marketing-ads/inputs/your_brand/logo.png"
COMP="marketing-ads/inputs/competitor"
ASPECT="9:16"                                    # <-- primary format
RUN_ID="$(basename "$RUN")"

mkdir -p "$RUN/candidates" "$RUN/accepted" "$RUN/audit"

for v in v1 v2 v3; do                            # <-- variation list
  # Optional per-variation competitor LAYOUT reference (structure only, fully restyled).
  # Remove this case block if competitor refs are not used for this campaign.
  case "$v" in
    v1) LAYOUT="$COMP/img2.jpg" ;;
    v2) LAYOUT="$COMP/img3.jpg" ;;
    v3) LAYOUT="$COMP/img4.jpg" ;;
    *)  LAYOUT="" ;;
  esac

  REF=()
  [ -f "$LOGO" ] && REF+=(--ref "$LOGO")
  [ -n "${LAYOUT:-}" ] && [ -f "$LAYOUT" ] && REF+=(--ref "$LAYOUT")

  echo "=== CREATE $v (layout ref: ${LAYOUT:-none}) ==="
  python3 "$SK/gen_image.py" --prompt-file "$RUN/prompts/$v.txt" \
      --out "$RUN/candidates/$v.png" --aspect "$ASPECT" ${REF[@]+"${REF[@]}"}

  echo "=== AUDIT $v ==="
  if python3 "$SK/audit_image.py" --image "$RUN/candidates/$v.png" \
      --csv "$RUN/audit/audit.csv" --brief "$RUN/brief.md" \
      --brand-profile "$BRAND" --run-id "$RUN_ID" --round 1; then
    cp "$RUN/candidates/$v.png" "$RUN/accepted/$v.png"
    echo ">> $v PASSED — copied to accepted/"
  else
    echo ">> $v FAILED audit — see audit.csv (regenerate with fixes)"
  fi
done

echo ""
echo "Done. Accepted images: $RUN/accepted/   Audit log: $RUN/audit/audit.csv"
