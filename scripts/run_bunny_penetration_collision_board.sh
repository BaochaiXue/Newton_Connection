#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_CASE="${ROOT}/scripts/run_bunny_force_case.py"
RENDER_BOARD="${ROOT}/scripts/render_bunny_penetration_collision_board.py"
PYTHON="${ROOT}/Newton/newton/.venv/bin/python"
RUN_ID="${1:-$(date +%Y%m%d_%H%M%S)_collision_force_board}"
if [[ $# -gt 0 ]]; then
  shift
fi

RESULT_ROOT="${ROOT}/results/bunny_force_visualization"
RUN_DIR="${RESULT_ROOT}/runs/${RUN_ID}"
BOX_ROOT="${RUN_DIR}/artifacts/box_control"
BUNNY_ROOT="${RUN_DIR}/artifacts/bunny_baseline"
BOARD_ROOT="${RUN_DIR}/artifacts/collision_force_board"
LOG_PATH="${RUN_DIR}/run.log"

mkdir -p "${BOX_ROOT}/phenomenon" "${BUNNY_ROOT}/phenomenon" "${BOARD_ROOT}" "${RUN_DIR}/logs"

COMMON=(
  --frames 80
  --sim-dt 0.0016666666666666668
  --substeps 10
  --render-fps 24
  --slowdown 1.0
  --screen-width 960
  --screen-height 540
  --force-diagnostic
  --no-stop-after-diagnostic
  --no-parity-check
  --defer-force-artifacts
  --post-contact-video-seconds 1.0
  --auto-set-weight 0.1
  --rigid-mass 0.5
  --drop-height 0.2
  --initial-velocity-z -1.0
)

BOX_BUNDLE="${BOX_ROOT}/phenomenon/force_diagnostic/force_render_bundle.pkl"
BUNNY_BUNDLE="${BUNNY_ROOT}/phenomenon/force_diagnostic/force_render_bundle.pkl"

cat > "${RUN_DIR}/command.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
bash "${ROOT}/scripts/run_bunny_penetration_collision_board.sh" "${RUN_ID}" "\$@"
EOF
chmod +x "${RUN_DIR}/command.sh"

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

run_case box_control "${BOX_ROOT}/phenomenon" --rigid-shape box "$@"
run_case bunny_baseline "${BUNNY_ROOT}/phenomenon" --rigid-shape bunny --bunny-scale 0.12 "$@"

{
  echo "[render_board] command=${PYTHON} ${RENDER_BOARD} --box-bundle ${BOX_BUNDLE} --bunny-bundle ${BUNNY_BUNDLE} --out-dir ${BOARD_ROOT}"
} | tee -a "${LOG_PATH}"
PYTHONPATH="${ROOT}/Newton/newton" \
  "${PYTHON}" "${RENDER_BOARD}" \
  --box-bundle "${BOX_BUNDLE}" \
  --bunny-bundle "${BUNNY_BUNDLE}" \
  --out-dir "${BOARD_ROOT}" 2>&1 | tee -a "${LOG_PATH}"

python - <<PY
from pathlib import Path
import json

run_dir = Path(${RUN_DIR@Q})
board_root = run_dir / "artifacts" / "collision_force_board"
box_root = run_dir / "artifacts" / "box_control" / "phenomenon"
bunny_root = run_dir / "artifacts" / "bunny_baseline" / "phenomenon"

def first_match(root: Path, pattern: str) -> str:
    matches = sorted(root.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"missing {pattern} under {root}")
    return str(matches[0])

summary = {
    "run_id": run_dir.name,
    "goal": "Per-frame all-contact-node penalty/total force board for box+bunny OFF cases.",
    "artifacts": {
        "board_video": str(board_root / "collision_force_board_2x2.mp4"),
        "board_summary": str(board_root / "summary.json"),
        "box_summary": first_match(box_root, "*_summary.json"),
        "bunny_summary": first_match(bunny_root, "*_summary.json"),
        "box_video": first_match(box_root, "*.mp4"),
        "bunny_video": first_match(bunny_root, "*.mp4"),
    },
}
(run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
readme = [
    "# Bunny Penetration Collision Board",
    "",
    "- Scope: self-collision OFF, box control + bunny baseline.",
    "- Main output: `artifacts/collision_force_board/collision_force_board_2x2.mp4`",
    "- Semantics:",
    "  - top-left: box penalty force on all cloth nodes colliding with box",
    "  - top-right: box total force on the same contact-node set",
    "  - bottom-left: bunny penalty force on all cloth nodes colliding with bunny",
    "  - bottom-right: bunny total force on the same contact-node set",
    "",
    "## Files",
    "",
    f"- summary: `{run_dir / 'summary.json'}`",
    f"- board summary: `{board_root / 'summary.json'}`",
    f"- board video: `{board_root / 'collision_force_board_2x2.mp4'}`",
]
(run_dir / "README.md").write_text("\\n".join(readme) + "\\n", encoding="utf-8")
PY

echo
echo "Artifacts:"
echo "  Run root: ${RUN_DIR}"
echo "  Command: ${RUN_DIR}/command.sh"
echo "  Log: ${LOG_PATH}"
echo "  Box bundle: ${BOX_BUNDLE}"
echo "  Bunny bundle: ${BUNNY_BUNDLE}"
echo "  Board video: ${BOARD_ROOT}/collision_force_board_2x2.mp4"
echo "  Board summary: ${BOARD_ROOT}/summary.json"
