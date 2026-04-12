#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/native_robot_table_penetration_probe_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/native_robot_probe_test --num-frames 180 --penetration-target-z 0.03

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
  echo "[run_native_robot_table_penetration_probe] root=${ROOT}"
  echo "[run_native_robot_table_penetration_probe] out_dir=${OUT_DIR}"
  echo "[run_native_robot_table_penetration_probe] command=${CMD[*]}"
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
echo "  MP4: ${OUT_DIR}/penetration_probe.mp4"
echo "  GIF: ${OUT_DIR}/penetration_probe.gif"
echo "  Contact sheet: ${OUT_DIR}/contact_sheet.jpg"
