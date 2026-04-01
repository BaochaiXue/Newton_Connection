#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEWTON_ROOT="${ROOT}/Newton"
SCRIPT="${NEWTON_ROOT}/phystwin_bridge/demos/demo_robot_rope_franka.py"
VALIDATOR="${ROOT}/scripts/validate_robot_rope_franka_hero.py"
RESULT_ROOT="${NEWTON_ROOT}/phystwin_bridge/results/robot_rope_franka"
STAMP="$(date +%Y%m%d_%H%M%S)"
SHORT_TAG="${SHORT_TAG:-default}"
if [[ "${1:-}" == "--tag" ]]; then
  SHORT_TAG="${2:-default}"
  shift 2
fi
RUN_ID="${STAMP}_${SHORT_TAG}"
RUN_DIR="${RESULT_ROOT}/candidates/${RUN_ID}"
PRESENT_DIR="${RUN_DIR}/presentation/work"
DEBUG_DIR="${RUN_DIR}/debug/work"
VALIDATION_DIR="${RUN_DIR}/validation/work"
SIM_DIR="${RUN_DIR}/sim/history"

mkdir -p "${PRESENT_DIR}" "${DEBUG_DIR}" "${VALIDATION_DIR}" "${SIM_DIR}"

RUN_COMMAND_TXT="${RUN_DIR}/run_command.txt"
STDOUT_LOG="${RUN_DIR}/stdout.log"
STDERR_LOG="${RUN_DIR}/stderr.log"
GIT_REV_TXT="${RUN_DIR}/git_rev.txt"
ENV_TXT="${RUN_DIR}/env.txt"
MANUAL_REVIEW_JSON="${RUN_DIR}/manual_review.json"

COMMON_ARGS=(
  --task tabletop_push_hero
  --sim-dt 5.0e-5
  --substeps 667
  --slowdown 1.0
  --render-fps 30
  --screen-width 1280
  --screen-height 720
  --viewer-headless
  --no-make-gif
  --anchor-count-per-end 2
  --tabletop-control-mode joint_trajectory
  --ik-target-blend 0.20
  --auto-set-weight 3.0
  --tabletop-initial-pose tabletop_curve
  --tabletop-preroll-settle-seconds 2.0
  --tabletop-preroll-damping-scale 6.0
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
  --tabletop-robot-base-offset -0.56 -0.22 0.10
  --tabletop-push-start-offset -0.09 -0.01 0.0
  --tabletop-push-contact-offset -0.04 -0.03 0.0
  --tabletop-push-end-offset 0.03 -0.04 0.0
  --tabletop-retract-offset -0.02 -0.02 0.0
  --tabletop-approach-clearance-z 0.10
  --tabletop-contact-clearance-z 0.010
  --tabletop-push-clearance-z 0.008
  --tabletop-retract-clearance-z 0.05
  --tabletop-ee-offset-z 0.22
  "$@"
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
  "${COMMON_ARGS[@]}"
)

VALIDATION_CMD=(
  python "${SCRIPT}"
  --out-dir "${VALIDATION_DIR}"
  --prefix robot_rope_tabletop_hero_validation
  --render-mode presentation
  --camera-profile validation
  "${COMMON_ARGS[@]}"
)

{
  printf '%q ' "${PRESENT_CMD[@]}"; printf '\n'
  printf '%q ' "${DEBUG_CMD[@]}"; printf '\n'
  printf '%q ' "${VALIDATION_CMD[@]}"; printf '\n'
} > "${RUN_COMMAND_TXT}"

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
  echo "[run_robot_rope_franka_tabletop_hero] run_dir=${RUN_DIR}"
  echo "[run_robot_rope_franka_tabletop_hero] presentation=${PRESENT_CMD[*]}"
  echo "[run_robot_rope_franka_tabletop_hero] debug=${DEBUG_CMD[*]}"
  echo "[run_robot_rope_franka_tabletop_hero] validation=${VALIDATION_CMD[*]}"
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

if [[ -f "${RUN_DIR}/presentation/physics_validation.json" ]]; then
  cp -f "${RUN_DIR}/presentation/physics_validation.json" "${RUN_DIR}/physics_validation.json"
elif [[ -f "${RUN_DIR}/presentation/work/physics_validation.json" ]]; then
  cp -f "${RUN_DIR}/presentation/work/physics_validation.json" "${RUN_DIR}/physics_validation.json"
elif [[ -f "${RUN_DIR}/presentation/physics_validation.json" ]]; then
  cp -f "${RUN_DIR}/presentation/physics_validation.json" "${RUN_DIR}/physics_validation.json"
fi

find "${PRESENT_DIR}" -maxdepth 1 -name '*.npy' -exec cp -f {} "${SIM_DIR}/" \;

VALIDATION_RC=0
python "${VALIDATOR}" "${RUN_DIR}" --manual-review-json "${MANUAL_REVIEW_JSON}" || VALIDATION_RC=$?

if [[ ! -f "${RUN_DIR}/manifest.json" ]]; then
  cat > "${RUN_DIR}/manifest.json" <<EOF
{
  "run_id": "${RUN_ID}",
  "task": "robot_rope_franka_tabletop_push_hero",
  "status": "candidate",
  "run_command_txt": "run_command.txt",
  "videos": {
    "hero_presentation": "hero_presentation.mp4",
    "hero_debug": "hero_debug.mp4",
    "validation_camera": "validation_camera.mp4"
  },
  "artifacts": {
    "summary_json": "summary.json",
    "metrics_json": "metrics.json",
    "validation_md": "validation.md",
    "ffprobe_json": "ffprobe.json",
    "contact_sheet": "contact_sheet.png",
    "keyframes_dir": "keyframes/"
  }
}
EOF
fi

echo
echo "Candidate run directory:"
echo "  ${RUN_DIR}"
echo "Key outputs:"
echo "  ${RUN_DIR}/hero_presentation.mp4"
echo "  ${RUN_DIR}/hero_debug.mp4"
echo "  ${RUN_DIR}/validation_camera.mp4"
echo "  ${RUN_DIR}/metrics.json"
echo "  ${RUN_DIR}/validation.md"
echo "Validator exit code:"
echo "  ${VALIDATION_RC}"
echo "Manual review template:"
echo "  ${MANUAL_REVIEW_JSON}"
