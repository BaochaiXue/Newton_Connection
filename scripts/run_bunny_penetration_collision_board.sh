#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_CASE="${ROOT}/scripts/run_bunny_force_case.py"
BUILD_DETECTOR="${ROOT}/scripts/build_bunny_collision_force_bundle.py"
RENDER_BOARD="${ROOT}/scripts/render_bunny_penetration_collision_board.py"
VALIDATE_VIS="${ROOT}/scripts/validate_bunny_force_visualization.py"
VALIDATE_ART="${ROOT}/scripts/validate_experiment_artifacts.py"
PYTHON="${ROOT}/Newton/newton/.venv/bin/python"
RUN_ID="${1:-$(date +%Y%m%d_%H%M%S)_realtime_allcolliding_2x2_v1}"
if [[ $# -gt 0 ]]; then
  shift
fi

RESULT_ROOT="${ROOT}/results/bunny_force_visualization"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
BOX_ROOT="${RUN_DIR}/artifacts/box_control"
BUNNY_ROOT="${RUN_DIR}/artifacts/bunny_baseline"
BOARD_ROOT="${RUN_DIR}/artifacts/collision_force_board"
LOG_PATH="${RUN_DIR}/run.log"
LATEST_ATTEMPT="${RESULT_ROOT}/LATEST_ATTEMPT.txt"
LATEST_SUCCESS="${RESULT_ROOT}/LATEST_SUCCESS.txt"

mkdir -p "${BOX_ROOT}/phenomenon" "${BOX_ROOT}/detector" "${BUNNY_ROOT}/phenomenon" "${BUNNY_ROOT}/detector" "${BOARD_ROOT}" "${RUN_DIR}/logs"
printf '%s\n' "${RUN_DIR}" > "${LATEST_ATTEMPT}"

COMMON=(
  --frames 80
  --sim-dt 0.0016666666666666668
  --substeps 10
  --render-fps 24
  --slowdown 1.0
  --screen-width 640
  --screen-height 360
  --force-diagnostic
  --no-stop-after-diagnostic
  --no-parity-check
  --defer-force-artifacts
  --post-contact-video-seconds 0
  --auto-set-weight 0.1
  --rigid-mass 0.5
  --drop-height 0.2
  --initial-velocity-z -1.0
)

BOX_BUNDLE="${BOX_ROOT}/phenomenon/force_diagnostic/force_render_bundle.pkl"
BUNNY_BUNDLE="${BUNNY_ROOT}/phenomenon/force_diagnostic/force_render_bundle.pkl"
BOX_DETECTOR_SUMMARY="${BOX_ROOT}/detector/summary.json"
BUNNY_DETECTOR_SUMMARY="${BUNNY_ROOT}/detector/summary.json"

cat > "${RUN_DIR}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_bunny_penetration_collision_board.sh" "${RUN_ID}" "\$@"
EOF
chmod +x "${RUN_DIR}/command.sh"

{
  echo "# Bunny Penetration Collision Board"
  echo
  echo "- Run id: \`${RUN_ID}\`"
  echo "- Goal: replace the old accepted bunny meeting artifact with a real-time all-colliding-node 2x2 board."
  echo "- Scope:"
  echo "  - self-collision OFF"
  echo "  - box_control"
  echo "  - bunny_baseline"
  echo "- Panel semantics:"
  echo "  - top-left: box penalty"
  echo "  - top-right: box total"
  echo "  - bottom-left: bunny penalty"
  echo "  - bottom-right: bunny total"
  echo "- Force definitions:"
  echo "  - penalty = f_external_total"
  echo "  - total = f_internal_total + f_external_total + mass * gravity_vec"
  echo "  - drag note: drag is excluded when applied as a post-step velocity correction rather than an accumulated force"
} > "${RUN_DIR}/README.md"

{
  echo "[run_bunny_penetration_collision_board] root=${ROOT}"
  echo "[run_bunny_penetration_collision_board] run_dir=${RUN_DIR}"
  echo "[run_bunny_penetration_collision_board] case_common=${COMMON[*]}"
  echo "[run_bunny_penetration_collision_board] extra_args=$*"
} | tee "${LOG_PATH}"

run_case() {
  local case_name="$1"
  local phenomenon_dir="$2"
  shift 2
  {
    echo "[run_case] case=${case_name}"
    echo "[run_case] out_dir=${phenomenon_dir}"
    echo "[run_case] command=${PYTHON} ${RUN_CASE} --out-dir ${phenomenon_dir} ${COMMON[*]} $*"
  } | tee -a "${LOG_PATH}"
  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${RUN_CASE}" \
    --out-dir "${phenomenon_dir}" \
    "${COMMON[@]}" \
    "$@" 2>&1 | tee -a "${LOG_PATH}"
}

build_detector() {
  local bundle_path="$1"
  local detector_dir="$2"
  {
    echo "[build_detector] bundle=${bundle_path}"
    echo "[build_detector] out_dir=${detector_dir}"
  } | tee -a "${LOG_PATH}"
  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${BUILD_DETECTOR}" \
    --bundle "${bundle_path}" \
    --out-dir "${detector_dir}" \
    --post-contact-seconds 1.0 2>&1 | tee -a "${LOG_PATH}"
}

run_case box_control "${BOX_ROOT}/phenomenon" --rigid-shape box "$@"
run_case bunny_baseline "${BUNNY_ROOT}/phenomenon" --rigid-shape bunny --bunny-scale 0.12 "$@"

build_detector "${BOX_BUNDLE}" "${BOX_ROOT}/detector"
build_detector "${BUNNY_BUNDLE}" "${BUNNY_ROOT}/detector"

{
  echo "[render_board] command=${PYTHON} ${RENDER_BOARD} --box-detector-summary ${BOX_DETECTOR_SUMMARY} --bunny-detector-summary ${BUNNY_DETECTOR_SUMMARY} --out-dir ${BOARD_ROOT}"
} | tee -a "${LOG_PATH}"
PYTHONPATH="${ROOT}/Newton/newton" \
  "${PYTHON}" "${RENDER_BOARD}" \
  --box-detector-summary "${BOX_DETECTOR_SUMMARY}" \
  --bunny-detector-summary "${BUNNY_DETECTOR_SUMMARY}" \
  --out-dir "${BOARD_ROOT}" 2>&1 | tee -a "${LOG_PATH}"

"${PYTHON}" "${VALIDATE_VIS}" --run-dir "${RUN_DIR}" 2>&1 | tee -a "${LOG_PATH}"
"${PYTHON}" "${VALIDATE_ART}" "${RUN_DIR}" --require-video --require-diagnostic --require-qa --summary-field board_video --summary-field detector_summaries 2>&1 | tee -a "${LOG_PATH}"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
board_summary = json.loads((run_dir / "artifacts" / "collision_force_board" / "summary.json").read_text(encoding="utf-8"))
box_summary = json.loads((run_dir / "artifacts" / "box_control" / "detector" / "summary.json").read_text(encoding="utf-8"))
bunny_summary = json.loads((run_dir / "artifacts" / "bunny_baseline" / "detector" / "summary.json").read_text(encoding="utf-8"))
qa_report = json.loads((run_dir / "qa" / "report.json").read_text(encoding="utf-8"))
overall_verdict = str(qa_report.get("overall_verdict", "FAIL"))

summary = {
    "run_id": run_dir.name,
    "goal": "Real-time all-colliding-node 2x2 bunny penetration board.",
    "board_video": str(run_dir / "artifacts" / "collision_force_board" / "collision_force_board_2x2.mp4"),
    "board_summary": str(run_dir / "artifacts" / "collision_force_board" / "summary.json"),
    "detector_summaries": {
        "box_control": str(run_dir / "artifacts" / "box_control" / "detector" / "summary.json"),
        "bunny_baseline": str(run_dir / "artifacts" / "bunny_baseline" / "detector" / "summary.json"),
    },
    "first_force_contact_frame_index": {
        "box_control": box_summary.get("first_force_contact_frame_index"),
        "bunny_baseline": bunny_summary.get("first_force_contact_frame_index"),
    },
    "validator_report": str(run_dir / "qa" / "report.json"),
    "validator_verdict": str(run_dir / "qa" / "verdict.md"),
    "overall_verdict": overall_verdict,
    "panel_semantics": board_summary.get("panel_semantics", {}),
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(overall_verdict)
PY

STATUS="$(python - <<PY
from pathlib import Path
import json
run_dir = Path(${RUN_DIR@Q})
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
print(summary.get("overall_verdict", "FAIL"))
PY
)"

if [[ "${STATUS}" == "PASS" ]]; then
  printf '%s\n' "${RUN_DIR}" > "${LATEST_SUCCESS}"
fi

echo
echo "Artifacts:"
echo "  Run root: ${RUN_DIR}"
echo "  Command: ${RUN_DIR}/command.sh"
echo "  Log: ${LOG_PATH}"
echo "  Box detector: ${BOX_DETECTOR_SUMMARY}"
echo "  Bunny detector: ${BUNNY_DETECTOR_SUMMARY}"
echo "  Board video: ${BOARD_ROOT}/collision_force_board_2x2.mp4"
echo "  QA report: ${RUN_DIR}/qa/report.json"
echo "  QA verdict: ${RUN_DIR}/qa/verdict.md"
echo "  Status: ${STATUS}"
