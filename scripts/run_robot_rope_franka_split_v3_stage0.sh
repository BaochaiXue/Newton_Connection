#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEWTON_ROOT="${ROOT}/Newton"
SCRIPT="${NEWTON_ROOT}/phystwin_bridge/demos/demo_robot_rope_franka_split_v3_stage0.py"
DIAG_SCRIPT="${ROOT}/scripts/diagnose_robot_rope_physical_blocking.py"
BLOCK_VALIDATOR="${ROOT}/scripts/validate_robot_rope_franka_physical_blocking.py"
ARTIFACT_VALIDATOR="${ROOT}/scripts/validate_experiment_artifacts.py"
REVIEW_SCRIPT="${ROOT}/scripts/review_robot_rope_franka_split_v3_stage0.py"
RESULT_ROOT="${NEWTON_ROOT}/phystwin_bridge/results/robot_rope_franka_split_v3_stage0"

SHORT_TAG="${SHORT_TAG:-default}"
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      SHORT_TAG="${2:?missing tag}"
      shift 2
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ID="${STAMP}_${SHORT_TAG}"
RUN_DIR="${RESULT_ROOT}/candidates/${RUN_ID}"
PRESENT_DIR="${RUN_DIR}/presentation/work"
DEBUG_DIR="${RUN_DIR}/debug/work"
VALIDATION_DIR="${RUN_DIR}/validation/work"
SIM_DIR="${RUN_DIR}/sim/history"
DIAG_DIR="${RUN_DIR}/diagnostics"
mkdir -p "${PRESENT_DIR}" "${DEBUG_DIR}" "${VALIDATION_DIR}" "${SIM_DIR}" "${DIAG_DIR}"

RUN_COMMAND_TXT="${RUN_DIR}/run_command.txt"
STDOUT_LOG="${RUN_DIR}/stdout.log"
STDERR_LOG="${RUN_DIR}/stderr.log"
ENV_TXT="${RUN_DIR}/env.txt"
GIT_REV_TXT="${RUN_DIR}/git_rev.txt"

COMMON_ARGS=(
  --task tabletop_push_hero
  --blocking-stage rigid_only
  --tabletop-control-mode robot_first_native
  --sim-dt 5.0e-5
  --substeps 667
  --slowdown 1.0
  --render-fps 30
  --screen-width 1280
  --screen-height 720
  --viewer-headless
  --no-make-gif
  --joint-target-ke 650.0
  --joint-target-kd 100.0
  --finger-target-ke 40.0
  --finger-target-kd 10.0
  --solver-iterations 15
  --solver-ls-iterations 100
  --default-body-armature 0.1
  --default-joint-armature 0.1
  --ignore-urdf-inertial-definitions
  --robot-base-pos -0.56 -0.22 0.10
  --table-center -0.02 -0.19 0.18
  --table-hx 0.20
  --table-hy 0.16
  --table-hz 0.02
  --ee-yaw-deg -18.0
  --settle-seconds 0.60
  --pre-seconds 0.50
  --approach-seconds 1.00
  --contact-seconds 0.40
  --push-seconds 1.20
  --retract-seconds 1.20
  --contact-depth 0.015
  --push-x-shift 0.06
  --retract-lift-z 0.08
)
COMMON_ARGS+=("${EXTRA_ARGS[@]}")

PRESENT_CMD=(
  python "${SCRIPT}"
  --out-dir "${PRESENT_DIR}"
  --prefix robot_rope_tabletop_hero
  --render-mode presentation
  --camera-profile hero
  "${COMMON_ARGS[@]}"
)

DEBUG_CMD=(
  python "${SCRIPT}"
  --out-dir "${DEBUG_DIR}"
  --prefix robot_rope_tabletop_hero_debug
  --render-mode debug
  --camera-profile hero
  --overlay-label
  --load-history-from-dir "${PRESENT_DIR}"
  --load-history-prefix robot_rope_tabletop_hero
  "${COMMON_ARGS[@]}"
)

VALIDATION_CMD=(
  python "${SCRIPT}"
  --out-dir "${VALIDATION_DIR}"
  --prefix robot_rope_tabletop_hero_validation
  --render-mode presentation
  --camera-profile validation
  --load-history-from-dir "${PRESENT_DIR}"
  --load-history-prefix robot_rope_tabletop_hero
  "${COMMON_ARGS[@]}"
)

{
  printf '%q ' "${PRESENT_CMD[@]}"; printf '\n'
  printf '%q ' "${DEBUG_CMD[@]}"; printf '\n'
  printf '%q ' "${VALIDATION_CMD[@]}"; printf '\n'
} > "${RUN_COMMAND_TXT}"
cp -f "${RUN_COMMAND_TXT}" "${RUN_DIR}/command.txt"

env | sort > "${ENV_TXT}"
if git -C "${NEWTON_ROOT}" rev-parse HEAD > "${GIT_REV_TXT}" 2>/dev/null; then
  :
else
  printf 'unavailable\n' > "${GIT_REV_TXT}"
fi

{
  echo "[run_robot_rope_franka_split_v3_stage0] run_dir=${RUN_DIR}"
  echo "[run_robot_rope_franka_split_v3_stage0] presentation=${PRESENT_CMD[*]}"
  echo "[run_robot_rope_franka_split_v3_stage0] debug=${DEBUG_CMD[*]}"
  echo "[run_robot_rope_franka_split_v3_stage0] validation=${VALIDATION_CMD[*]}"
} | tee "${STDOUT_LOG}"

"${PRESENT_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
"${DEBUG_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
"${VALIDATION_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"

cp -f "${PRESENT_DIR}/robot_rope_tabletop_hero.mp4" "${RUN_DIR}/hero_presentation.mp4"
cp -f "${DEBUG_DIR}/robot_rope_tabletop_hero_debug.mp4" "${RUN_DIR}/hero_debug.mp4"
cp -f "${VALIDATION_DIR}/robot_rope_tabletop_hero_validation.mp4" "${RUN_DIR}/validation_camera.mp4"

SUMMARY_SRC="$(find "${PRESENT_DIR}" -maxdepth 1 -name '*_summary.json' | head -n 1)"
if [[ -n "${SUMMARY_SRC}" ]]; then
  cp -f "${SUMMARY_SRC}" "${RUN_DIR}/summary.json"
  cp -f "${SUMMARY_SRC}" "${RUN_DIR}/stage0_summary.json"
fi
if [[ -f "${PRESENT_DIR}/physics_validation.json" ]]; then
  cp -f "${PRESENT_DIR}/physics_validation.json" "${RUN_DIR}/physics_validation.json"
fi

find "${PRESENT_DIR}" -maxdepth 1 -name '*.npy' -exec cp -f {} "${SIM_DIR}/" \;

python "${DIAG_SCRIPT}" "${RUN_DIR}" --out-dir "${DIAG_DIR}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
cp -f "${DIAG_DIR}/robot_table_contact_report.json" "${RUN_DIR}/robot_table_contact_report.json"
cp -f "${DIAG_DIR}/nonfinger_table_contact_report.json" "${RUN_DIR}/nonfinger_table_contact_report.json"
cp -f "${DIAG_DIR}/robot_table_penetration_plot.png" "${RUN_DIR}/robot_table_penetration_plot.png"
cp -f "${DIAG_DIR}/robot_table_contact_sheet.png" "${RUN_DIR}/robot_table_contact_sheet.png"
cp -f "${DIAG_DIR}/nonfinger_table_penetration_plot.png" "${RUN_DIR}/nonfinger_table_penetration_plot.png"
if [[ -f "${DIAG_DIR}/collider_inventory.json" ]]; then
  cp -f "${DIAG_DIR}/collider_inventory.json" "${RUN_DIR}/collider_inventory.json"
fi

python - "${RUN_DIR}" <<'PY'
import json, pathlib, sys
run_dir = pathlib.Path(sys.argv[1])
summary_path = run_dir / "summary.json"
if not summary_path.exists():
    raise SystemExit(0)
summary = json.loads(summary_path.read_text())
for name in ["robot_table_contact_report.json", "nonfinger_table_contact_report.json"]:
    path = run_dir / name
    if path.exists():
        summary.update(json.loads(path.read_text()))
summary_path.write_text(json.dumps(summary, indent=2))
(run_dir / "stage0_summary.json").write_text(json.dumps(summary, indent=2))
PY

python "${REVIEW_SCRIPT}" "${RUN_DIR}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}" || true

BLOCK_RC=0
python "${BLOCK_VALIDATOR}" "${RUN_DIR}" || BLOCK_RC=$?
cp -f "${RUN_DIR}/blocking_metrics.json" "${RUN_DIR}/metrics.json"
cp -f "${RUN_DIR}/blocking_validation.md" "${RUN_DIR}/validation.md"
cp -f "${RUN_DIR}/validation.md" "${RUN_DIR}/stage0_validation.md"

cat > "${RUN_DIR}/geometry_truth_report.md" <<EOF
# Geometry Truth Report

- visible contactor: \`native Franka finger geometry\`
- proof surface: \`actual_multi_box_finger_colliders\`
- visible tool enabled: \`false\`
- support box enabled: \`false\`
- blocking stage: \`rigid_only\`
- hidden helper: \`NO\`
- renderer history source: \`same-history presentation rollout\`
EOF

cat > "${RUN_DIR}/README.md" <<EOF
# robot_rope_franka_split_v3_stage0

This candidate is the split_v3 Stage-0 robot-first direct-finger blocking run.

- native Newton Franka
- native Newton table
- no rope
- no support box
- no visible tool
- same-history hero/debug/validation
EOF

cat > "${RUN_DIR}/manifest.json" <<EOF
{
  "run_id": "${RUN_ID}",
  "task": "robot_rope_franka_split_v3_stage0",
  "status": "candidate",
  "videos": {
    "hero_presentation": "hero_presentation.mp4",
    "hero_debug": "hero_debug.mp4",
    "validation_camera": "validation_camera.mp4"
  },
  "artifacts": {
    "summary_json": "summary.json",
    "stage0_summary_json": "stage0_summary.json",
    "metrics_json": "metrics.json",
    "validation_md": "validation.md",
    "multimodal_review_md": "multimodal_review.md",
    "geometry_truth_report_md": "geometry_truth_report.md",
    "early_settle_sheet_jpg": "early_settle_sheet.jpg",
    "first_contact_sheet_jpg": "first_contact_sheet.jpg",
    "contact_sheet_jpg": "contact_sheet.jpg"
  }
}
EOF

ARTIFACT_RC=0
python "${ARTIFACT_VALIDATOR}" "${RUN_DIR}" --require-video || ARTIFACT_RC=$?

echo
echo "Candidate run directory:"
echo "  ${RUN_DIR}"
echo "Key outputs:"
echo "  ${RUN_DIR}/hero_presentation.mp4"
echo "  ${RUN_DIR}/hero_debug.mp4"
echo "  ${RUN_DIR}/validation_camera.mp4"
echo "  ${RUN_DIR}/early_settle_sheet.jpg"
echo "  ${RUN_DIR}/first_contact_sheet.jpg"
echo "  ${RUN_DIR}/contact_sheet.jpg"
echo "  ${RUN_DIR}/multimodal_review.md"
echo "  ${RUN_DIR}/metrics.json"
echo "Validator exit codes:"
echo "  blocking=${BLOCK_RC}"
echo "  artifact=${ARTIFACT_RC}"
