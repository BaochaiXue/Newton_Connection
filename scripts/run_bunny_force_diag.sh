#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
DEFAULT_OUT_DIR="${ROOT}/tmp/bunny_force_diag_${STAMP}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [out_dir] [extra args...]

Examples:
  $(basename "$0")
  $(basename "$0") ${ROOT}/tmp/my_diag --rigid-shape box --drop-height 0.10

Default workflow:
  - bunny target
  - force diagnostic enabled
  - parity check enabled
  - hybrid top-k selection
  - normal-only snapshot render
  - stop after diagnostic trigger

Artifacts will be written inside:
  <out_dir>/self_off/
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
  --rigid-shape bunny
  --force-diagnostic
  --parity-check
  --force-topk-mode hybrid
  --force-render-mode normal_only
  --force-snapshot-frame trigger
  --stop-after-diagnostic
  "$@"
)

{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  printf '%q ' "${CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"
chmod +x "${COMMAND_TXT}"

{
  echo "[run_bunny_force_diag] root=${ROOT}"
  echo "[run_bunny_force_diag] out_dir=${OUT_DIR}"
  echo "[run_bunny_force_diag] command=${CMD[*]}"
} | tee "${LOG_TXT}"

"${CMD[@]}" 2>&1 | tee -a "${LOG_TXT}"

echo
echo "Artifacts:"
echo "  Output root: ${OUT_DIR}/self_off"
echo "  Command: ${COMMAND_TXT}"
echo "  Log: ${LOG_TXT}"
echo "  Expected diagnostic summary: ${OUT_DIR}/self_off/force_diagnostic/force_diag_trigger_summary.json"
echo "  Expected diagnostic NPZ: ${OUT_DIR}/self_off/force_diagnostic/force_diag_trigger_substep.npz"
echo "  Expected snapshot PNG: ${OUT_DIR}/self_off/force_diagnostic/force_diag_trigger_snapshot.png"
