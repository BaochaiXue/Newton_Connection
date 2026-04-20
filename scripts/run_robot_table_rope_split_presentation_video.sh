#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="${ROOT}/scripts/run_robot_table_rope_split_demo.sh"
REVIEW_BUNDLE_SCRIPT="${ROOT}/scripts/prepare_video_review_bundle.py"
AUDIT_SCRIPT="${ROOT}/scripts/run_skeptical_video_audit.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/robot_table_rope_split_presentation_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra demo args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/robot_table_rope_split_presentation_debug --width 1280 --height 720

This wrapper:
  1. runs the presentation-oriented split demo
  2. prepares a skeptical-review bundle
  3. runs skeptical audit if review_bundle/manual_review.json exists

Artifacts will be written inside:
  <out_dir>/
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

OUT_DIR="${1:-${DEFAULT_OUT_DIR}}"
if [[ $# -gt 0 ]]; then
  shift
fi

bash "${WRAPPER}" "${OUT_DIR}" \
  --coupling-mode one_way \
  --video-mode presentation_lifted \
  --num-frames 0 \
  "$@"

REVIEW_DIR="${OUT_DIR}/review_bundle"
python "${REVIEW_BUNDLE_SCRIPT}" \
  --video "${OUT_DIR}/hero.mp4" \
  --out-dir "${REVIEW_DIR}"

CLAIM_TXT="${REVIEW_DIR}/claim.txt"
cat > "${CLAIM_TXT}" <<'EOF'
The split demo presentation video is acceptable as a meeting-facing artifact because it conservatively shows robot finger/pad approach, visible finger-rope contact, and rope response in one complete process window.
EOF

MANUAL_REVIEW_TEMPLATE="${REVIEW_DIR}/manual_review_template.json"
cat > "${MANUAL_REVIEW_TEMPLATE}" <<'EOF'
{
  "verdict": "FAIL",
  "claim_boundary": "The split demo presentation video is acceptable as a meeting-facing artifact because it conservatively shows robot finger/pad approach, visible finger-rope contact, and rope response in one complete process window.",
  "evidence": []
}
EOF

if [[ -f "${REVIEW_DIR}/manual_review.json" ]]; then
  python "${AUDIT_SCRIPT}" \
    --review-bundle "${REVIEW_DIR}" \
    --claim-file "${CLAIM_TXT}" \
    --manual-review-json "${REVIEW_DIR}/manual_review.json"
else
  echo
  echo "Prepared skeptical review bundle:"
  echo "  Review bundle: ${REVIEW_DIR}"
  echo "  Claim text: ${CLAIM_TXT}"
  echo "  Manual review template: ${MANUAL_REVIEW_TEMPLATE}"
  echo "  Add review_bundle/manual_review.json and rerun:"
  echo "    python ${AUDIT_SCRIPT} --review-bundle ${REVIEW_DIR} --claim-file ${CLAIM_TXT} --manual-review-json ${REVIEW_DIR}/manual_review.json"
fi
