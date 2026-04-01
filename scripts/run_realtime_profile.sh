#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/realtime_profile_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/profile_box --mode off --rigid-shape box

Default workflow:
  - viewer disabled (null)
  - profile-only mode
  - 1 warmup run
  - 5 measured runs
  - 300 frames per run

Artifacts will be written directly under:
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
mkdir -p "${OUT_DIR}"

COMMAND_TXT="${OUT_DIR}/command.sh"
LOG_TXT="${OUT_DIR}/run.log"

CMD=(
  python "${SCRIPT}"
  --viewer null
  --profile-only
  --profile-runs 5
  --profile-warmup-runs 1
  --num-frames 300
  --out-dir "${OUT_DIR}"
  "$@"
)

{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  printf '%q ' "${CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"
chmod +x "${COMMAND_TXT}"

{
  echo "[run_realtime_profile] root=${ROOT}"
  echo "[run_realtime_profile] out_dir=${OUT_DIR}"
  echo "[run_realtime_profile] command=${CMD[*]}"
} | tee "${LOG_TXT}"

"${CMD[@]}" 2>&1 | tee -a "${LOG_TXT}"

echo
echo "Artifacts:"
echo "  Output root: ${OUT_DIR}"
echo "  Command: ${COMMAND_TXT}"
echo "  Log: ${LOG_TXT}"
echo "  Expected profile JSON: ${OUT_DIR}/cloth_bunny_playground_profile.json"
echo "  Expected profile CSV: ${OUT_DIR}/cloth_bunny_playground_profile.csv"
