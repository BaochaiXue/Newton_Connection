#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEWTON_ROOT="${ROOT}/Newton"
SCRIPT="${NEWTON_ROOT}/phystwin_bridge/demos/demo_robot_rope_franka.py"
BLOCK_VALIDATOR="${ROOT}/scripts/validate_robot_rope_franka_physical_blocking.py"
ARTIFACT_VALIDATOR="${ROOT}/scripts/validate_experiment_artifacts.py"
DIAG_SCRIPT="${ROOT}/scripts/diagnose_robot_rope_physical_blocking.py"
RESULT_ROOT="${NEWTON_ROOT}/phystwin_bridge/results/robot_rope_franka_physical_blocking"

BLOCKING_STAGE="rigid_only"
SHORT_TAG="${SHORT_TAG:-default}"
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      SHORT_TAG="${2:-default}"
      shift 2
      ;;
    --blocking-stage)
      BLOCKING_STAGE="${2:?missing blocking stage}"
      shift 2
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ID="${STAMP}_${BLOCKING_STAGE}_${SHORT_TAG}"
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
GIT_REV_TXT="${RUN_DIR}/git_rev.txt"
ENV_TXT="${RUN_DIR}/env.txt"
MANUAL_REVIEW_JSON="${RUN_DIR}/manual_review.json"

COMMON_ARGS=(
  --task tabletop_push_hero
  --blocking-stage "${BLOCKING_STAGE}"
  --tabletop-control-mode joint_target_drive
  --sim-dt 5.0e-5
  --substeps 667
  --slowdown 1.0
  --render-fps 30
  --screen-width 1280
  --screen-height 720
  --viewer-headless
  --no-make-gif
  --anchor-count-per-end 2
  --ik-target-blend 0.20
  --auto-set-weight 3.0
  --joint-target-ke 100.0
  --joint-target-kd 10.0
  --finger-target-ke 20.0
  --finger-target-kd 2.0
  --solver-joint-attach-ke 50.0
  --solver-joint-attach-kd 5.0
  --default-body-armature 0.01
  --default-joint-armature 0.01
  --ignore-urdf-inertial-definitions
  --visible-tool-mode none
  --tabletop-initial-pose tabletop_shallow_curve
  --tabletop-hero-hide-pedestal
  --tabletop-preroll-settle-seconds 3.5
  --tabletop-preroll-damping-scale 2.5
  --tabletop-settle-seconds 0.8
  --tabletop-approach-seconds 1.4
  --tabletop-push-seconds 2.4
  --tabletop-hold-seconds 0.4
  --tabletop-retract-seconds 1.2
  --tabletop-rope-height 0.156
  --tabletop-table-top-z 0.200
  --tabletop-table-hx 0.42
  --tabletop-table-hy 0.24
  --tabletop-table-hz 0.020
  --tabletop-robot-base-offset -0.54 -0.20 0.06
  --tabletop-push-start-offset -0.09 -0.01 0.0
  --tabletop-push-contact-offset -0.04 -0.03 0.0
  --tabletop-push-end-offset 0.03 -0.04 0.0
  --tabletop-retract-offset -0.02 -0.02 0.0
  --tabletop-approach-clearance-z 0.10
  --tabletop-contact-clearance-z 0.010
  --tabletop-push-clearance-z 0.008
  --tabletop-retract-clearance-z 0.05
  --tabletop-ee-offset-z 0.22
  --particle-radius-scale 0.1
  --rope-line-width 0.024
  "${EXTRA_ARGS[@]}"
)

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

cat > "${MANUAL_REVIEW_JSON}" <<'EOF'
{
  "output_complete": false,
  "robot_is_native_newton_asset": false,
  "table_is_present_and_supportive": false,
  "rope_is_resting_on_or_interacting_with_table_before_push": false,
  "robot_contacts_rope": false,
  "rope_deforms_due_to_contact": false,
  "rope_moves_after_contact_not_before": false,
  "contact_zone_is_readable": false,
  "no_obvious_penetration_or_teleporting": false,
  "presentation_ready": false
}
EOF

{
  echo "[run_robot_rope_franka_physical_blocking] run_dir=${RUN_DIR}"
  echo "[run_robot_rope_franka_physical_blocking] stage=${BLOCKING_STAGE}"
  echo "[run_robot_rope_franka_physical_blocking] presentation=${PRESENT_CMD[*]}"
  echo "[run_robot_rope_franka_physical_blocking] debug=${DEBUG_CMD[*]}"
  echo "[run_robot_rope_franka_physical_blocking] validation=${VALIDATION_CMD[*]}"
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
fi

if [[ -f "${RUN_DIR}/presentation/work/physics_validation.json" ]]; then
  cp -f "${RUN_DIR}/presentation/work/physics_validation.json" "${RUN_DIR}/physics_validation.json"
elif [[ -f "${RUN_DIR}/presentation/physics_validation.json" ]]; then
  cp -f "${RUN_DIR}/presentation/physics_validation.json" "${RUN_DIR}/physics_validation.json"
fi

find "${PRESENT_DIR}" -maxdepth 1 -name '*.npy' -exec cp -f {} "${SIM_DIR}/" \;

python "${DIAG_SCRIPT}" "${RUN_DIR}" --out-dir "${DIAG_DIR}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
cp -f "${DIAG_DIR}/robot_table_contact_report.json" "${RUN_DIR}/robot_table_contact_report.json"
cp -f "${DIAG_DIR}/ee_target_vs_actual_plot.png" "${RUN_DIR}/ee_target_vs_actual_plot.png"
cp -f "${DIAG_DIR}/robot_table_penetration_plot.png" "${RUN_DIR}/robot_table_penetration_plot.png"
cp -f "${DIAG_DIR}/robot_table_contact_sheet.png" "${RUN_DIR}/robot_table_contact_sheet.png"

BLOCK_RC=0
python "${BLOCK_VALIDATOR}" "${RUN_DIR}" || BLOCK_RC=$?
cp -f "${RUN_DIR}/blocking_metrics.json" "${RUN_DIR}/metrics.json"
cp -f "${RUN_DIR}/blocking_validation.md" "${RUN_DIR}/validation.md"

cat > "${RUN_DIR}/README.md" <<EOF
# robot_rope_franka_physical_blocking

Stage: \`${BLOCKING_STAGE}\`

This candidate uses the native Franka direct-finger path with \`joint_target_drive\`
as the controller truth surface. hero/debug/validation are rendered from one
saved rollout history. The final proof surface is the actual imported Franka
finger-box collider set against the native tabletop box.
EOF

cat > "${RUN_DIR}/manifest.json" <<EOF
{
  "run_id": "${RUN_ID}",
  "task": "robot_rope_franka_physical_blocking",
  "blocking_stage": "${BLOCKING_STAGE}",
  "status": "candidate",
  "run_command_txt": "run_command.txt",
  "videos": {
    "hero_presentation": "hero_presentation.mp4",
    "hero_debug": "hero_debug.mp4",
    "validation_camera": "validation_camera.mp4"
  },
  "artifacts": {
    "summary_json": "summary.json",
    "physics_validation_json": "physics_validation.json",
    "robot_table_contact_report_json": "robot_table_contact_report.json",
    "ee_target_vs_actual_plot_png": "ee_target_vs_actual_plot.png",
    "robot_table_penetration_plot_png": "robot_table_penetration_plot.png",
    "robot_table_contact_sheet_png": "robot_table_contact_sheet.png",
    "diagnostics_dir": "diagnostics/"
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
echo "  ${RUN_DIR}/robot_table_contact_report.json"
echo "  ${RUN_DIR}/blocking_metrics.json"
echo "Validator exit codes:"
echo "  blocking=${BLOCK_RC}"
echo "  artifact=${ARTIFACT_RC}"
