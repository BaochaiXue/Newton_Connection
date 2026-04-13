#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/robot_table_rope_split_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/robot_table_rope_split_debug --num-frames 120 --coupling-mode one_way

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

if [[ -e "${OUT_DIR}" ]]; then
  rm -rf "${OUT_DIR}"
fi
mkdir -p "${OUT_DIR}"

COMMAND_TXT="${OUT_DIR}/command.sh"
LOG_TXT="${OUT_DIR}/run.log"

CMD=(
  python "${SCRIPT}"
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
  echo "[run_robot_table_rope_split_demo] root=${ROOT}"
  echo "[run_robot_table_rope_split_demo] out_dir=${OUT_DIR}"
  echo "[run_robot_table_rope_split_demo] command=${CMD[*]}"
} | tee "${LOG_TXT}"

"${CMD[@]}" 2>&1 | tee -a "${LOG_TXT}"

echo
echo "Artifacts:"
echo "  Output root: ${OUT_DIR}"
echo "  Command: ${COMMAND_TXT}"
echo "  Log: ${LOG_TXT}"
echo "  Summary: ${OUT_DIR}/summary.json"
echo "  Scene: ${OUT_DIR}/scene.npz"
echo "  Timeseries: ${OUT_DIR}/timeseries.csv"
echo "  MP4: ${OUT_DIR}/hero.mp4"
echo "  GIF: ${OUT_DIR}/hero.gif"
echo "  Contact sheet: ${OUT_DIR}/contact_sheet.jpg"
