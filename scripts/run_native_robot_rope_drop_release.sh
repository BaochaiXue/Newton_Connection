#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${ROOT}/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py"
PHYSICS_VALIDATOR="${ROOT}/scripts/validate_robot_rope_drop_release_physics.py"
VIDEO_VALIDATOR="${ROOT}/scripts/validate_native_robot_rope_drop_release_video.py"
RESULT_ROOT="${ROOT}/results/native_robot_rope_drop_release"
STAMP="$(date +%Y%m%d_%H%M%S)"
SLUG="drop_release_drag_on"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [--slug <slug>] [extra demo args...]

This wrapper runs the native Franka drop/release baseline twice:
  1. presentation render
  2. debug render

It writes the canonical bundle under:
  ${RESULT_ROOT}/runs/<timestamp>_native_franka_<slug>/

Default demo settings:
  --task drop_release_baseline
  --slowdown 1.0
  --render-fps 30
  --anchor-height 1.02
  --anchor-count-per-end 2
  --ik-target-blend 0.35
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--slug" ]]; then
  if [[ -z "${2:-}" ]]; then
    echo "--slug requires a value" >&2
    exit 2
  fi
  SLUG="${2}"
  shift 2
fi

RUN_ID="${STAMP}_native_franka_${SLUG}"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
PRESENT_DIR="${RUN_DIR}/presentation"
DEBUG_DIR="${RUN_DIR}/debug"
PRESENT_WORK="${PRESENT_DIR}/work"
DEBUG_WORK="${DEBUG_DIR}/work"
SIM_DIR="${RUN_DIR}/sim/history"
QA_DIR="${RUN_DIR}/qa"
KEYFRAMES_DIR="${RUN_DIR}/keyframes"

mkdir -p "${PRESENT_WORK}" "${DEBUG_WORK}" "${SIM_DIR}" "${QA_DIR}" "${KEYFRAMES_DIR}"

COMMAND_TXT="${RUN_DIR}/command.txt"
STDOUT_LOG="${RUN_DIR}/stdout.log"
STDERR_LOG="${RUN_DIR}/stderr.log"
NOTES_MD="${RUN_DIR}/notes.md"
ENV_TXT="${RUN_DIR}/env.txt"
GIT_REV_TXT="${RUN_DIR}/git_rev.txt"
README_MD="${RUN_DIR}/README.md"
MANIFEST_JSON="${RUN_DIR}/manifest.json"
INDEX_CSV="${RESULT_ROOT}/index.csv"
LATEST_ATTEMPT_TXT="${RESULT_ROOT}/LATEST_ATTEMPT.txt"

COMMON_ARGS=(
  --task drop_release_baseline
  --slowdown 1.0
  --render-fps 30
  --anchor-height 1.02
  --anchor-count-per-end 2
  --ik-target-blend 0.35
  --drop-approach-seconds 0.55
  --drop-support-seconds 0.40
  --drop-release-seconds 0.12
  --drop-freefall-seconds 1.80
  --gripper-hold 0.012
  --viewer-headless
  --no-make-gif
)

PRESENT_CMD=(
  python "${SCRIPT}"
  --out-dir "${PRESENT_WORK}"
  --prefix "robot_rope_drop_release"
  --render-mode presentation
  --camera-profile hero
  "${COMMON_ARGS[@]}"
  "$@"
)

DEBUG_CMD=(
  python "${SCRIPT}"
  --out-dir "${DEBUG_WORK}"
  --prefix "robot_rope_drop_release_debug"
  --render-mode debug
  --camera-profile validation
  --overlay-label
  "${COMMON_ARGS[@]}"
  "$@"
)

{
  echo "# Presentation"
  printf '%q ' "${PRESENT_CMD[@]}"
  printf '\n'
  echo
  echo "# Debug"
  printf '%q ' "${DEBUG_CMD[@]}"
  printf '\n'
} > "${COMMAND_TXT}"

env | sort > "${ENV_TXT}"
if git -C "${ROOT}/Newton" rev-parse HEAD > "${GIT_REV_TXT}" 2>/dev/null; then
  :
else
  printf 'unavailable\n' > "${GIT_REV_TXT}"
fi

{
  echo "# Notes"
  echo
  echo "- run_id: ${RUN_ID}"
  echo "- slug: ${SLUG}"
  echo "- task: drop_release_baseline"
  echo "- source_script: ${SCRIPT}"
} > "${NOTES_MD}"

{
  echo "[run_native_robot_rope_drop_release] root=${ROOT}"
  echo "[run_native_robot_rope_drop_release] run_dir=${RUN_DIR}"
  echo "[run_native_robot_rope_drop_release] presentation=${PRESENT_CMD[*]}"
  echo "[run_native_robot_rope_drop_release] debug=${DEBUG_CMD[*]}"
} | tee "${STDOUT_LOG}"

"${PRESENT_CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)
"${DEBUG_CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)

PRESENT_SUMMARY_SRC="$(find "${PRESENT_WORK}" -maxdepth 1 -name '*_summary.json' | head -n 1)"
PRESENT_MP4_SRC="$(find "${PRESENT_WORK}" -maxdepth 1 -name '*.mp4' | head -n 1)"
DEBUG_MP4_SRC="$(find "${DEBUG_WORK}" -maxdepth 1 -name '*.mp4' | head -n 1)"

if [[ -z "${PRESENT_SUMMARY_SRC}" || -z "${PRESENT_MP4_SRC}" || -z "${DEBUG_MP4_SRC}" ]]; then
  echo "Missing required outputs under ${RUN_DIR}" >&2
  exit 1
fi

cp "${PRESENT_SUMMARY_SRC}" "${RUN_DIR}/summary.json"
cp "${PRESENT_MP4_SRC}" "${RUN_DIR}/final_presentation.mp4"
cp "${DEBUG_MP4_SRC}" "${RUN_DIR}/final_debug.mp4"
find "${PRESENT_WORK}" -maxdepth 1 -name '*.npy' -exec cp {} "${SIM_DIR}/" \;

python "${PHYSICS_VALIDATOR}" "${RUN_DIR}" --output "${RUN_DIR}/physics_validation.json"
python "${VIDEO_VALIDATOR}" \
  "${RUN_DIR}" \
  --presentation-video "${RUN_DIR}/final_presentation.mp4" \
  --debug-video "${RUN_DIR}/final_debug.mp4" \
  --summary-json "${RUN_DIR}/summary.json" \
  --physics-validation-json "${RUN_DIR}/physics_validation.json"

cat > "${README_MD}" <<EOF
# Run README

- run_id: \`${RUN_ID}\`
- result bundle: \`results/native_robot_rope_drop_release\`
- task: \`drop_release_baseline\`
- presentation video: \`final_presentation.mp4\`
- debug video: \`final_debug.mp4\`
- summary: \`summary.json\`
- physics validation: \`physics_validation.json\`
- video verdict: \`qa/verdict.md\`

## Notes

- This wrapper records the presentation run as the authoritative physics source.
- The debug render is regenerated with the same settings except \`--render-mode debug\`.
- If this run becomes the accepted best run, update \`BEST_RUN.md\`, \`LATEST_SUCCESS.txt\`, and the slide source.
EOF

python - <<PY
from pathlib import Path
import csv
import json
run_dir = Path(${RUN_DIR@Q})
manifest = {
    "run_id": ${RUN_ID@Q},
    "status": "attempt",
    "result_bundle": "results/native_robot_rope_drop_release",
    "entrypoint": "scripts/run_native_robot_rope_drop_release.sh",
    "command_txt": "command.txt",
    "summary_json": "summary.json",
    "physics_validation_json": "physics_validation.json",
    "final_presentation_mp4": "final_presentation.mp4",
    "final_debug_mp4": "final_debug.mp4",
    "qa_dir": "qa",
    "keyframes_dir": "keyframes",
    "sim_history_dir": "sim/history",
}
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

index_csv = Path(${INDEX_CSV@Q})
if not index_csv.exists():
    index_csv.write_text("run_id,status,location,path,task,render_mode,notes\\n", encoding="utf-8")
with index_csv.open("a", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow([
        ${RUN_ID@Q},
        "attempt",
        "results",
        str(run_dir),
        "drop_release_baseline",
        "presentation+debug",
        "Canonical wrapper run; physics and video validators executed",
    ])
PY

printf '%s\n' "${RUN_DIR}" > "${LATEST_ATTEMPT_TXT}"

echo
echo "Canonical run created:"
echo "  ${RUN_DIR}"
echo "Key files:"
echo "  ${RUN_DIR}/summary.json"
echo "  ${RUN_DIR}/physics_validation.json"
echo "  ${RUN_DIR}/final_presentation.mp4"
echo "  ${RUN_DIR}/final_debug.mp4"
echo "  ${RUN_DIR}/qa/verdict.md"
