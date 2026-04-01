#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LATEST_ATTEMPT_FILE="${ROOT}/results/bunny_force_visualization/LATEST_ATTEMPT.txt"
DEFAULT_RUN_DIR="$(cat "${LATEST_ATTEMPT_FILE}")"
RUN_DIR="${1:-${DEFAULT_RUN_DIR}}"
if [[ $# -gt 0 ]]; then
  shift
fi

if [[ "${RUN_DIR}" != /* ]]; then
  RUN_DIR="${ROOT}/${RUN_DIR}"
fi

mkdir -p "${RUN_DIR}/qa"

COMMAND_TXT="${RUN_DIR}/qa/command.sh"
LOG_TXT="${RUN_DIR}/qa/run.log"

CMD=(
  python "${ROOT}/scripts/validate_bunny_force_visualization.py"
  --run-dir "${RUN_DIR}"
  --sample-count 12
  "$@"
)

{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  printf '%q ' "${CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"
chmod +x "${COMMAND_TXT}"

{
  echo "[run_bunny_force_visualization_qa] root=${ROOT}"
  echo "[run_bunny_force_visualization_qa] run_dir=${RUN_DIR}"
  echo "[run_bunny_force_visualization_qa] command=${CMD[*]}"
} | tee "${LOG_TXT}"

"${CMD[@]}" 2>&1 | tee -a "${LOG_TXT}"

python "${ROOT}/scripts/validate_experiment_artifacts.py" "${RUN_DIR}" --require-qa 2>&1 | tee -a "${LOG_TXT}"

echo
echo "Artifacts:"
echo "  QA root: ${RUN_DIR}/qa"
echo "  Command: ${COMMAND_TXT}"
echo "  Log: ${LOG_TXT}"
echo "  Report: ${RUN_DIR}/qa/report.json"
echo "  Verdict: ${RUN_DIR}/qa/verdict.md"
echo "  Contact sheets: ${RUN_DIR}/qa/contact_sheets/"
echo "  Sampled frames: ${RUN_DIR}/qa/sampled_frames/"
