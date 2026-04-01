#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py"
VALIDATOR="${ROOT}/scripts/validate_robot_deformable_demo.py"
GIT_ROOT="${ROOT}/Newton"
STAMP="$(date +%Y%m%d_%H%M%S)"
TASK="lift_release"
RENDER_MODE="presentation"
RUN_ID="${STAMP}_native_franka_${TASK}_${RENDER_MODE}"
RUN_DIR="${ROOT}/results/robot_deformable_demo/runs/${RUN_ID}"
WORK_DIR="${RUN_DIR}/work"
MEDIA_DIR="${RUN_DIR}/media"
SIM_DIR="${RUN_DIR}/sim"
HISTORY_DIR="${SIM_DIR}/history"
QA_DIR="${RUN_DIR}/qa"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [extra args...]

This wrapper creates a canonical results run directory and then runs:
  ${SCRIPT}

Default preset:
  --task ${TASK}
  --render-mode ${RENDER_MODE}
  --make-gif

Artifacts are organized under:
  ${ROOT}/results/robot_deformable_demo/runs/<timestamp>_native_franka_${TASK}_${RENDER_MODE}/
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

mkdir -p "${WORK_DIR}" "${MEDIA_DIR}" "${HISTORY_DIR}" "${QA_DIR}"

COMMAND_TXT="${RUN_DIR}/command.txt"
STDOUT_LOG="${RUN_DIR}/stdout.log"
STDERR_LOG="${RUN_DIR}/stderr.log"
GIT_REV_TXT="${RUN_DIR}/git_rev.txt"
ENV_TXT="${RUN_DIR}/env.txt"
NOTES_MD="${RUN_DIR}/notes.md"

CMD=(
  python "${SCRIPT}"
  --out-dir "${WORK_DIR}"
  --prefix robot_push_rope_franka
  --task "${TASK}"
  --render-mode "${RENDER_MODE}"
  --make-gif
  "$@"
)

{
  printf '%q ' "${CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"
if git -C "${GIT_ROOT}" rev-parse HEAD > "${GIT_REV_TXT}" 2>/dev/null; then
  :
else
  printf 'unavailable\n' > "${GIT_REV_TXT}"
fi
env | sort > "${ENV_TXT}"

{
  echo "# Notes"
  echo
  echo "- run_id: ${RUN_ID}"
  echo "- task: ${TASK}"
  echo "- render_mode: ${RENDER_MODE}"
  echo "- source_script: ${SCRIPT}"
} > "${NOTES_MD}"

{
  echo "[run_robot_rope_franka] root=${ROOT}"
  echo "[run_robot_rope_franka] run_dir=${RUN_DIR}"
  echo "[run_robot_rope_franka] command=${CMD[*]}"
} | tee "${STDOUT_LOG}"

"${CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)

SUMMARY_SRC="$(find "${WORK_DIR}" -maxdepth 1 -name '*_summary.json' | head -n 1)"
MP4_SRC="$(find "${WORK_DIR}" -maxdepth 1 -name '*.mp4' | head -n 1)"
GIF_SRC="$(find "${WORK_DIR}" -maxdepth 1 -name '*.gif' | head -n 1)"

if [[ -z "${SUMMARY_SRC}" || -z "${MP4_SRC}" ]]; then
  echo "Missing summary or mp4 in ${WORK_DIR}" >&2
  exit 1
fi

cp "${SUMMARY_SRC}" "${RUN_DIR}/summary.json"
cp "${MP4_SRC}" "${MEDIA_DIR}/final.mp4"
if [[ -n "${GIF_SRC}" ]]; then
  cp "${GIF_SRC}" "${MEDIA_DIR}/preview.gif"
fi

find "${WORK_DIR}" -maxdepth 1 -name '*.npy' -exec cp {} "${HISTORY_DIR}/" \;

python "${VALIDATOR}" "${RUN_DIR}" --video "${MEDIA_DIR}/final.mp4" --summary "${RUN_DIR}/summary.json"

python - <<PY
from pathlib import Path
import json
run_dir = Path(${RUN_DIR@Q})
manifest = {
    "run_id": ${RUN_ID@Q},
    "task": ${TASK@Q},
    "render_mode": ${RENDER_MODE@Q},
    "source_script": ${SCRIPT@Q},
    "command_txt": str(run_dir / "command.txt"),
    "stdout_log": str(run_dir / "stdout.log"),
    "stderr_log": str(run_dir / "stderr.log"),
    "summary_json": str(run_dir / "summary.json"),
    "final_mp4": str(run_dir / "media" / "final.mp4"),
    "preview_gif": str(run_dir / "media" / "preview.gif"),
    "ffprobe_json": str(run_dir / "qa" / "ffprobe.json"),
    "contact_sheet": str(run_dir / "qa" / "contact_sheet.png"),
    "event_sheet": str(run_dir / "qa" / "event_sheet.png"),
    "validation_json": str(run_dir / "qa" / "validation.json"),
    "verdict_md": str(run_dir / "qa" / "verdict.md"),
}
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo
echo "Canonical run created:"
echo "  ${RUN_DIR}"
echo "Key files:"
echo "  ${RUN_DIR}/summary.json"
echo "  ${MEDIA_DIR}/final.mp4"
echo "  ${QA_DIR}/ffprobe.json"
echo "  ${QA_DIR}/contact_sheet.png"
echo "  ${QA_DIR}/event_sheet.png"
echo "  ${QA_DIR}/validation.json"
echo "  ${QA_DIR}/verdict.md"
