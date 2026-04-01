#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DETECTOR="${ROOT}/scripts/build_bunny_collision_force_bundle.py"
RENDER_BOARD="${ROOT}/scripts/render_bunny_penetration_collision_board.py"
VALIDATE_VIS="${ROOT}/scripts/validate_bunny_force_visualization.py"
VALIDATE_ART="${ROOT}/scripts/validate_experiment_artifacts.py"
PYTHON="${ROOT}/Newton/newton/.venv/bin/python"
SYS_PYTHON="python"
SOURCE_RUN_DEFAULT="${ROOT}/results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2"

RUN_ID="${1:-$(date +%Y%m%d_%H%M%S)_realtime_allcolliding_2x2_v1}"
if [[ $# -gt 0 ]]; then
  shift
fi

SOURCE_RUN="${SOURCE_RUN_DEFAULT}"
BOX_BUNDLE=""
BUNNY_BUNDLE=""
FORCE_PERCENTILE="98.0"
MAX_ARROW_WORLD_LEN="0.04"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-run)
      SOURCE_RUN="$(realpath "$2")"
      shift 2
      ;;
    --box-bundle)
      BOX_BUNDLE="$(realpath "$2")"
      shift 2
      ;;
    --bunny-bundle)
      BUNNY_BUNDLE="$(realpath "$2")"
      shift 2
      ;;
    --force-percentile)
      FORCE_PERCENTILE="$2"
      shift 2
      ;;
    --max-arrow-world-len)
      MAX_ARROW_WORLD_LEN="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${BOX_BUNDLE}" ]]; then
  BOX_BUNDLE="${SOURCE_RUN}/artifacts/matrix/box_control/phenomenon/force_diagnostic/force_render_bundle.pkl"
fi
if [[ -z "${BUNNY_BUNDLE}" ]]; then
  BUNNY_BUNDLE="${SOURCE_RUN}/artifacts/matrix/bunny_baseline/phenomenon/force_diagnostic/force_render_bundle.pkl"
fi

RESULT_ROOT="${ROOT}/results/bunny_force_visualization"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
CASE_ROOT="${RUN_DIR}/artifacts/source_cases"
BOX_ROOT="${CASE_ROOT}/box_control"
BUNNY_ROOT="${CASE_ROOT}/bunny_baseline"
BOARD_ROOT="${RUN_DIR}/artifacts/collision_force_board"
QA_ROOT="${RUN_DIR}/qa"
LOG_DIR="${RUN_DIR}/logs"
LOG_PATH="${LOG_DIR}/run.log"
LATEST_ATTEMPT="${RESULT_ROOT}/LATEST_ATTEMPT.txt"
LATEST_SUCCESS="${RESULT_ROOT}/LATEST_SUCCESS.txt"
INDEX_MD="${RESULT_ROOT}/INDEX.md"

mkdir -p "${BOX_ROOT}" "${BUNNY_ROOT}" "${BOARD_ROOT}" "${QA_ROOT}" "${LOG_DIR}" "${RUN_DIR}/src_patch_summary"
printf '%s\n' "${RUN_DIR}" > "${LATEST_ATTEMPT}"

cat > "${RUN_DIR}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_bunny_penetration_collision_board.sh" "${RUN_ID}" --source-run "${SOURCE_RUN}" --force-percentile "${FORCE_PERCENTILE}" --max-arrow-world-len "${MAX_ARROW_WORLD_LEN}"
EOF
chmod +x "${RUN_DIR}/command.sh"

cat > "${RUN_DIR}/RUN_STATE.md" <<EOF
# Run State

- state: in_progress
- run_id: ${RUN_ID}
- goal: meeting-readable self-collision-OFF 2x2 board over all rigid force-active cloth nodes
EOF

cat > "${RUN_DIR}/NEXT_ACTION.txt" <<EOF
Run detectors, render the 2x2 board, validate it, then promote only if QA passes.
EOF

cat > "${RUN_DIR}/FAILURE_LOG.md" <<EOF
# Failure Log

- none yet
EOF

cat > "${RUN_DIR}/SUCCESS_CHECKLIST.md" <<EOF
# Success Checklist

- [ ] self-collision OFF for both source cases
- [ ] detector bundle saved per frame for box
- [ ] detector bundle saved per frame for bunny
- [ ] final 2x2 board video exists
- [ ] validator passes
- [ ] artifact validator passes
- [ ] docs/status updated
EOF

{
  echo "[run_bunny_penetration_collision_board] root=${ROOT}"
  echo "[run_bunny_penetration_collision_board] run_dir=${RUN_DIR}"
  echo "[run_bunny_penetration_collision_board] source_run=${SOURCE_RUN}"
  echo "[run_bunny_penetration_collision_board] box_bundle=${BOX_BUNDLE}"
  echo "[run_bunny_penetration_collision_board] bunny_bundle=${BUNNY_BUNDLE}"
  echo "[run_bunny_penetration_collision_board] force_percentile=${FORCE_PERCENTILE}"
  echo "[run_bunny_penetration_collision_board] max_arrow_world_len=${MAX_ARROW_WORLD_LEN}"
} | tee "${LOG_PATH}"

build_detector() {
  local case_name="$1"
  local bundle_path="$2"
  local out_dir="$3"
  {
    echo "[build_detector] case=${case_name}"
    echo "[build_detector] bundle=${bundle_path}"
    echo "[build_detector] out_dir=${out_dir}"
  } | tee -a "${LOG_PATH}"
  PYTHONPATH="${ROOT}/Newton/newton" \
    "${PYTHON}" "${BUILD_DETECTOR}" \
    --bundle "${bundle_path}" \
    --out-dir "${out_dir}" \
    --post-contact-seconds 1.0 2>&1 | tee -a "${LOG_PATH}"
}

build_detector "box_control" "${BOX_BUNDLE}" "${BOX_ROOT}"
build_detector "bunny_baseline" "${BUNNY_BUNDLE}" "${BUNNY_ROOT}"

{
  echo "[render_board] board_out_dir=${BOARD_ROOT}"
  echo "[render_board] box_detector_summary=${BOX_ROOT}/summary.json"
  echo "[render_board] bunny_detector_summary=${BUNNY_ROOT}/summary.json"
} | tee -a "${LOG_PATH}"
PYTHONPATH="${ROOT}/Newton/newton" \
  "${SYS_PYTHON}" "${RENDER_BOARD}" \
  --box-detector-summary "${BOX_ROOT}/summary.json" \
  --bunny-detector-summary "${BUNNY_ROOT}/summary.json" \
  --out-dir "${BOARD_ROOT}" \
  --force-percentile "${FORCE_PERCENTILE}" \
  --max-arrow-world-len "${MAX_ARROW_WORLD_LEN}" 2>&1 | tee -a "${LOG_PATH}"

python - <<PY
from pathlib import Path
import json
import shutil

run_dir = Path(${RUN_DIR@Q})
case_root = run_dir / "artifacts" / "source_cases"
for case_name in ("box_control", "bunny_baseline"):
    det_summary = json.loads((case_root / case_name / "summary.json").read_text(encoding="utf-8"))
    source_scene = Path(det_summary["source_scene_path"])
    source_summary = Path(det_summary["source_summary_path"])
    for src, dst_name in (
        (source_scene, f"{case_name}_scene.npz"),
        (source_summary, f"{case_name}_source_summary.json"),
    ):
        dst = run_dir / dst_name
        if src.exists():
            shutil.copy2(src, dst)
PY

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
board_summary = json.loads((run_dir / "artifacts" / "collision_force_board" / "summary.json").read_text(encoding="utf-8"))
box_summary = json.loads((run_dir / "artifacts" / "source_cases" / "box_control" / "summary.json").read_text(encoding="utf-8"))
bunny_summary = json.loads((run_dir / "artifacts" / "source_cases" / "bunny_baseline" / "summary.json").read_text(encoding="utf-8"))

summary = {
    "run_id": run_dir.name,
    "goal": "Real-time all-colliding-node self-collision-OFF 2x2 board for cloth+box and cloth+bunny.",
    "board_video": str(run_dir / "artifacts" / "collision_force_board" / "collision_force_board_2x2.mp4"),
    "board_summary": str(run_dir / "artifacts" / "collision_force_board" / "summary.json"),
    "detector_summaries": {
        "box_control": str(run_dir / "artifacts" / "source_cases" / "box_control" / "summary.json"),
        "bunny_baseline": str(run_dir / "artifacts" / "source_cases" / "bunny_baseline" / "summary.json"),
    },
    "first_force_contact_frame_index": {
        "box_control": box_summary.get("first_force_contact_frame_index"),
        "bunny_baseline": bunny_summary.get("first_force_contact_frame_index"),
    },
    "force_definitions": board_summary.get("force_definitions", {}),
    "panel_semantics": board_summary.get("panel_semantics", {}),
    "node_mask_semantics": board_summary.get("node_mask_semantics", ""),
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
manifest = {
    "run_id": run_dir.name,
    "created_at": board_summary.get("generated_at", ""),
    "status": "attempt",
    "result_bundle": "results/bunny_force_visualization",
    "entrypoint": "scripts/run_bunny_penetration_collision_board.sh",
    "command": str(run_dir / "command.sh"),
    "code_paths": [
        "scripts/build_bunny_collision_force_bundle.py",
        "scripts/render_bunny_penetration_collision_board.py",
        "scripts/validate_bunny_force_visualization.py",
    ],
    "inputs": [
        ${BOX_BUNDLE@Q},
        ${BUNNY_BUNDLE@Q},
    ],
    "outputs": [
        str(run_dir / "summary.json"),
        str(run_dir / "artifacts" / "collision_force_board" / "collision_force_board_2x2.mp4"),
        str(run_dir / "qa" / "report.json"),
    ],
    "summary_path": "summary.json",
    "readme_path": "README.md",
    "artifacts": {
        "summary": "summary.json",
        "logs": "logs/",
        "qa": "qa/",
        "qa_report": "qa/report.json",
        "qa_verdict": "qa/verdict.md",
        "qa_contact_sheets": "qa/contact_sheets/",
        "qa_sampled_frames": "qa/sampled_frames/",
        "board": "artifacts/collision_force_board/",
        "cases": "artifacts/source_cases/",
    },
    "validation": {
        "validator": "scripts/validate_bunny_force_visualization.py + scripts/validate_experiment_artifacts.py",
        "status": "pending",
        "notes": ""
    },
    "notes": "Previous accepted bunny mechanism artifact is superseded for meeting visualization by this board run."
}
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
readme_lines = [
    "# Bunny Penetration Collision Board Run",
    "",
    "## Purpose",
    "",
    "Build the stricter meeting-facing self-collision-OFF 2x2 board over all rigid force-active cloth nodes.",
    "",
    "## Inputs",
    "",
    "- box source bundle: `${BOX_BUNDLE}`",
    "- bunny source bundle: `${BUNNY_BUNDLE}`",
    "",
    "## Outputs",
    "",
    f"- board video: `{run_dir / 'artifacts' / 'collision_force_board' / 'collision_force_board_2x2.mp4'}`",
    f"- board summary: `{run_dir / 'artifacts' / 'collision_force_board' / 'summary.json'}`",
    f"- box detector summary: `{run_dir / 'artifacts' / 'source_cases' / 'box_control' / 'summary.json'}`",
    f"- bunny detector summary: `{run_dir / 'artifacts' / 'source_cases' / 'bunny_baseline' / 'summary.json'}`",
    "",
    "## Main Semantics",
    "",
    "- top-left: box penalty",
    "- top-right: box total",
    "- bottom-left: bunny penalty",
    "- bottom-right: bunny total",
    "- main node set: rigid_force_contact_mask = geom_contact_mask AND force_contact_mask",
    "- penalty force: f_external_total on the current frame",
    "- total force: f_internal_total + f_external_total + mass * gravity_vec on the current frame",
]
(run_dir / "README.md").write_text("\\n".join(readme_lines) + "\\n", encoding="utf-8")
PY

PYTHONPATH="${ROOT}/Newton/newton" \
  "${SYS_PYTHON}" "${VALIDATE_VIS}" \
  --run-dir "${RUN_DIR}" \
  --video "${BOARD_ROOT}/collision_force_board_2x2.mp4" \
  --board-summary "${BOARD_ROOT}/summary.json" 2>&1 | tee -a "${LOG_PATH}"

PYTHONPATH="${ROOT}/Newton/newton" \
  "${SYS_PYTHON}" "${VALIDATE_ART}" \
  "${RUN_DIR}" \
  --require-video \
  --require-detector \
  --require-collision-board \
  --require-qa \
  --summary-field board_video \
  --summary-field detector_summaries 2>&1 | tee -a "${LOG_PATH}"

STATUS="$(python - <<PY
from pathlib import Path
import json
run_dir = Path(${RUN_DIR@Q})
qa = json.loads((run_dir / "qa" / "report.json").read_text(encoding="utf-8"))
print(qa.get("overall_verdict", "FAIL"))
PY
)"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
manifest["status"] = "success" if ${STATUS@Q} == "PASS" else "attempt"
manifest["validation"]["status"] = ${STATUS@Q}
manifest["validation"]["notes"] = str(run_dir / "qa" / "verdict.md")
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(run_dir / "RUN_STATE.md").write_text(
    "# Run State\\n\\n- state: " + ("passed" if ${STATUS@Q} == "PASS" else "failed") + "\\n- run_id: " + run_dir.name + "\\n",
    encoding="utf-8",
)
if ${STATUS@Q} == "PASS":
    (run_dir / "NEXT_ACTION.txt").write_text("Promoted as the latest meeting-facing bunny force board run.\\n", encoding="utf-8")
    (run_dir / "FAILURE_LOG.md").write_text("# Failure Log\\n\\n- none\\n", encoding="utf-8")
    (run_dir / "SUCCESS_CHECKLIST.md").write_text("# Success Checklist\\n\\n- [x] self-collision OFF for both source cases\\n- [x] detector bundles saved\\n- [x] final 2x2 board video exists\\n- [x] validators passed\\n- [x] ready to promote\\n", encoding="utf-8")
else:
    (run_dir / "NEXT_ACTION.txt").write_text("Inspect qa/verdict.md and collision_force_board summary before promotion.\\n", encoding="utf-8")
PY

if [[ "${STATUS}" == "PASS" ]]; then
  printf '%s\n' "${RUN_DIR}" > "${LATEST_SUCCESS}"
  cat > "${INDEX_MD}" <<EOF
# Bunny Force Visualization Index

- Latest success: \`${RUN_DIR}\`
- Main 2x2 board: \`${BOARD_ROOT}/collision_force_board_2x2.mp4\`
- Board summary: \`${BOARD_ROOT}/summary.json\`
- Run README: \`${RUN_DIR}/README.md\`

## Accepted Claims Under The All-Colliding-Node Board Contract
- The previous trigger-centered bunny mechanism artifact is superseded for meeting visualization purposes.
- The promoted board is self-collision OFF and scope-locked to:
  - cloth + box
  - cloth + bunny
- The main board shows every rigid force-active cloth node, not top-k only.
- Panel semantics are:
  - top-left = box penalty
  - top-right = box total
  - bottom-left = bunny penalty
  - bottom-right = bunny total
- Board timing runs from rollout start to one second after first force-active rigid collision.
EOF
fi

echo
echo "Artifacts:"
echo "  Run root: ${RUN_DIR}"
echo "  Command: ${RUN_DIR}/command.sh"
echo "  Log: ${LOG_PATH}"
echo "  Box detector: ${BOX_ROOT}/summary.json"
echo "  Bunny detector: ${BUNNY_ROOT}/summary.json"
echo "  Board video: ${BOARD_ROOT}/collision_force_board_2x2.mp4"
echo "  QA report: ${RUN_DIR}/qa/report.json"
echo "  QA verdict: ${RUN_DIR}/qa/verdict.md"
echo "  Status: ${STATUS}"
