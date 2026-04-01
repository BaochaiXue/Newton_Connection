#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-}"

if [[ -z "${RUN_DIR}" || "${RUN_DIR}" == "-h" || "${RUN_DIR}" == "--help" ]]; then
  cat <<EOF
Usage:
  $(basename "$0") <run_dir> [extra args...]

Example:
  $(basename "$0") ${ROOT}/tmp/demo_robot_rope_franka_lift_release_presentation_full
EOF
  exit 0
fi

shift

if [[ "${RUN_DIR}" != /* ]]; then
  RUN_DIR="${ROOT}/${RUN_DIR}"
fi

COMMAND_TXT="${RUN_DIR}/command_validate_robot_video.sh"
LOG_TXT="${RUN_DIR}/validation_run.log"

CMD=(
  python "${ROOT}/scripts/validate_robot_deformable_video.py"
  --run-dir "${RUN_DIR}"
  "$@"
)

{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  printf '%q ' "${CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"
chmod +x "${COMMAND_TXT}"

{
  echo "[run_robot_deformable_validation] root=${ROOT}"
  echo "[run_robot_deformable_validation] run_dir=${RUN_DIR}"
  echo "[run_robot_deformable_validation] command=${CMD[*]}"
} | tee "${LOG_TXT}"

"${CMD[@]}" 2>&1 | tee -a "${LOG_TXT}"
