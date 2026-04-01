#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${ROOT}/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py"
VALIDATOR="${ROOT}/scripts/validate_robot_rope_franka_hero.py"
RESULT_ROOT="${ROOT}/Newton/phystwin_bridge/results/robot_rope_franka"
STAMP="$(date +%Y%m%d_%H%M%S)"
SLUG="tabletop_hero"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [--slug name] [extra demo args...]

Runs the native Franka tabletop hero path in three modes:
  - hero presentation
  - hero debug
  - validation camera

Artifacts are written under:
  ${RESULT_ROOT}/candidates/<timestamp>_<slug>/
EOF
}

EXTRA_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --slug)
      SLUG="$2"
      shift 2
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

RUN_ID="${STAMP}_${SLUG}"
RUN_DIR="${RESULT_ROOT}/candidates/${RUN_ID}"
PRESENT_WORK="${RUN_DIR}/presentation/work"
DEBUG_WORK="${RUN_DIR}/debug/work"
VALIDATION_WORK="${RUN_DIR}/validation/work"
mkdir -p "${PRESENT_WORK}" "${DEBUG_WORK}" "${VALIDATION_WORK}"

RUN_COMMAND_TXT="${RUN_DIR}/run_command.txt"
STDOUT_LOG="${RUN_DIR}/stdout.log"
STDERR_LOG="${RUN_DIR}/stderr.log"
MANUAL_REVIEW_JSON="${RUN_DIR}/manual_review.json"

COMMON_ARGS=(
  --task tabletop_push_hero
  --viewer-headless
  --no-make-gif
  --screen-width 1280
  --screen-height 720
  --render-fps 30
  "${EXTRA_ARGS[@]}"
)

PRESENT_CMD=(
  python "${DEMO}"
  --out-dir "${PRESENT_WORK}"
  --prefix hero_presentation
  --render-mode presentation
  --camera-profile hero
  "${COMMON_ARGS[@]}"
)

DEBUG_CMD=(
  python "${DEMO}"
  --out-dir "${DEBUG_WORK}"
  --prefix hero_debug
  --render-mode debug
  --camera-profile hero
  --overlay-label
  "${COMMON_ARGS[@]}"
)

VALIDATION_CMD=(
  python "${DEMO}"
  --out-dir "${VALIDATION_WORK}"
  --prefix validation_camera
  --render-mode presentation
  --camera-profile validation
  "${COMMON_ARGS[@]}"
)

{
  echo "# run_robot_rope_franka_hero"
  echo
  printf "presentation: "
  printf '%q ' "${PRESENT_CMD[@]}"
  printf '\n'
  printf "debug: "
  printf '%q ' "${DEBUG_CMD[@]}"
  printf '\n'
  printf "validation: "
  printf '%q ' "${VALIDATION_CMD[@]}"
  printf '\n'
} > "${RUN_COMMAND_TXT}"

{
  echo "[run_robot_rope_franka_hero] root=${ROOT}"
  echo "[run_robot_rope_franka_hero] run_dir=${RUN_DIR}"
  echo "[run_robot_rope_franka_hero] presentation=${PRESENT_CMD[*]}"
  echo "[run_robot_rope_franka_hero] debug=${DEBUG_CMD[*]}"
  echo "[run_robot_rope_franka_hero] validation=${VALIDATION_CMD[*]}"
} | tee "${STDOUT_LOG}"

"${PRESENT_CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)
"${DEBUG_CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)
"${VALIDATION_CMD[@]}" > >(tee -a "${STDOUT_LOG}") 2> >(tee -a "${STDERR_LOG}" >&2)

cp -f "${PRESENT_WORK}/hero_presentation.mp4" "${RUN_DIR}/hero_presentation.mp4"
cp -f "${DEBUG_WORK}/hero_debug.mp4" "${RUN_DIR}/hero_debug.mp4"
cp -f "${VALIDATION_WORK}/validation_camera.mp4" "${RUN_DIR}/validation_camera.mp4"

cp -f "${PRESENT_WORK}/hero_presentation_summary.json" "${RUN_DIR}/summary.json"
cp -f "${RUN_DIR}/presentation/physics_validation.json" "${RUN_DIR}/physics_validation.json"

if [[ ! -f "${MANUAL_REVIEW_JSON}" ]]; then
  cat > "${MANUAL_REVIEW_JSON}" <<EOF
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
fi

python "${VALIDATOR}" "${RUN_DIR}" --manual-review-json "${MANUAL_REVIEW_JSON}"

echo
echo "Hero candidate written to:"
echo "  ${RUN_DIR}"
echo "Key files:"
echo "  ${RUN_DIR}/hero_presentation.mp4"
echo "  ${RUN_DIR}/hero_debug.mp4"
echo "  ${RUN_DIR}/validation_camera.mp4"
echo "  ${RUN_DIR}/summary.json"
echo "  ${RUN_DIR}/metrics.json"
echo "  ${RUN_DIR}/validation.md"
