#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_CASE="${ROOT}/scripts/run_bunny_force_case.py"
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
BOX_ROOT="${RUN_DIR}/artifacts/box_control/phenomenon"
BUNNY_ROOT="${RUN_DIR}/artifacts/bunny_baseline/phenomenon"
BOARD_ROOT="${RUN_DIR}/artifacts/collision_force_board"
LOG_PATH="${RUN_DIR}/run.log"
LATEST_ATTEMPT="${RESULT_ROOT}/LATEST_ATTEMPT.txt"
LATEST_SUCCESS="${RESULT_ROOT}/LATEST_SUCCESS.txt"

mkdir -p "${BOX_ROOT}" "${BUNNY_ROOT}" "${BOARD_ROOT}" "${RUN_DIR}/logs"
printf '%s\n' "${RUN_DIR}" > "${LATEST_ATTEMPT}"

COMMON=(
  --frames 80
  --sim-dt 0.0016666666666666668
  --substeps 10
  --render-fps 30
  --slowdown 1.0
  --screen-width 960
  --screen-height 540
  --force-diagnostic
  --no-stop-after-diagnostic
  --no-parity-check
  --skip-render
  --auto-set-weight 0.1
  --rigid-mass 0.5
  --drop-height 0.2
  --initial-velocity-z -1.0
)

BOX_DETECTOR_SUMMARY="${BOX_ROOT}/detector/summary.json"
BUNNY_DETECTOR_SUMMARY="${BUNNY_ROOT}/detector/summary.json"

cat > "${RUN_DIR}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_bunny_penetration_collision_board.sh" "${RUN_ID}"
EOF
chmod +x "${RUN_DIR}/command.sh"

cat > "${RUN_DIR}/README.md" <<EOF
# Bunny Penetration Collision Board Run

- scope: self-collision OFF, cloth+box, cloth+bunny
- final board semantics:
  - top-left: box penalty
  - top-right: box total
  - bottom-left: bunny penalty
  - bottom-right: bunny total
- penalty force definition: \`f_external_total\`
- total force definition: \`f_internal_total + f_external_total + mass * gravity_vec\`
EOF

{
  echo "[run_bunny_penetration_collision_board] root=${ROOT}"
  echo "[run_bunny_penetration_collision_board] run_dir=${RUN_DIR}"
  echo "[run_bunny_penetration_collision_board] common=${COMMON[*]}"
} | tee "${LOG_PATH}"

run_case() {
  local case_name="$1"
  local out_dir="$2"
  shift 2
  {
    echo "[run_case] case=${case_name}"
    echo "[run_case] out_dir=${out_dir}"
    echo "[run_case] command=${PYTHON} ${RUN_CASE} --out-dir ${out_dir} ${COMMON[*]} $*"
  } | tee -a "${LOG_PATH}"
  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${RUN_CASE}" \
    --out-dir "${out_dir}" \
    "${COMMON[@]}" \
    "$@" 2>&1 | tee -a "${LOG_PATH}"
}

run_case box_control "${BOX_ROOT}" --rigid-shape box
run_case bunny_baseline "${BUNNY_ROOT}" --rigid-shape bunny --bunny-scale 0.12

{
  echo "[render_board] box_detector_summary=${BOX_DETECTOR_SUMMARY}"
  echo "[render_board] bunny_detector_summary=${BUNNY_DETECTOR_SUMMARY}"
  echo "[render_board] out_dir=${BOARD_ROOT}"
} | tee -a "${LOG_PATH}"
PYTHONPATH="${ROOT}/Newton/newton" \
  "${PYTHON}" "${RENDER_BOARD}" \
  --box-detector-summary "${BOX_DETECTOR_SUMMARY}" \
  --bunny-detector-summary "${BUNNY_DETECTOR_SUMMARY}" \
  --out-dir "${BOARD_ROOT}" 2>&1 | tee -a "${LOG_PATH}"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
board_summary = json.loads((run_dir / "artifacts" / "collision_force_board" / "summary.json").read_text(encoding="utf-8"))
box_summary = json.loads((run_dir / "artifacts" / "box_control" / "phenomenon" / "detector" / "summary.json").read_text(encoding="utf-8"))
bunny_summary = json.loads((run_dir / "artifacts" / "bunny_baseline" / "phenomenon" / "detector" / "summary.json").read_text(encoding="utf-8"))
summary = {
    "run_id": run_dir.name,
    "goal": "Real-time all-colliding-node 2x2 bunny penetration board.",
    "board_video": str(run_dir / "artifacts" / "collision_force_board" / "collision_force_board_2x2.mp4"),
    "board_summary": str(run_dir / "artifacts" / "collision_force_board" / "summary.json"),
    "detector_summaries": {
        "box_control": str(run_dir / "artifacts" / "box_control" / "phenomenon" / "detector" / "summary.json"),
        "bunny_baseline": str(run_dir / "artifacts" / "bunny_baseline" / "phenomenon" / "detector" / "summary.json"),
    },
    "first_force_contact_frame_index": {
        "box_control": box_summary.get("first_force_contact_frame_index"),
        "bunny_baseline": bunny_summary.get("first_force_contact_frame_index"),
    },
    "force_definitions": board_summary.get("force_definitions", {}),
    "panel_semantics": board_summary.get("panel_semantics", {}),
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
PY

"${PYTHON}" "${VALIDATE_VIS}" --run-dir "${RUN_DIR}" 2>&1 | tee -a "${LOG_PATH}"
"${PYTHON}" "${VALIDATE_ART}" "${RUN_DIR}" --require-video --require-diagnostic --require-detector --require-collision-board --require-qa --summary-field board_video --summary-field detector_summaries 2>&1 | tee -a "${LOG_PATH}"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
qa_report = json.loads((run_dir / "qa" / "report.json").read_text(encoding="utf-8"))
summary["validator_report"] = str(run_dir / "qa" / "report.json")
summary["validator_verdict"] = str(run_dir / "qa" / "verdict.md")
summary["overall_verdict"] = str(qa_report.get("overall_verdict", "FAIL"))
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(summary["overall_verdict"])
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
echo "  Board video: ${BOARD_ROOT}/collision_force_board_2x2.mp4"
echo "  QA report: ${RUN_DIR}/qa/report.json"
echo "  QA verdict: ${RUN_DIR}/qa/verdict.md"
echo "  Status: ${STATUS}"
