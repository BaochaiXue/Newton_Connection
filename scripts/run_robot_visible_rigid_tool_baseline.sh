#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NEWTON_ROOT="${ROOT}/Newton"
SCRIPT="${NEWTON_ROOT}/phystwin_bridge/demos/demo_robot_rope_franka.py"
VALIDATOR="${ROOT}/scripts/validate_robot_rope_franka_hero.py"
DIAGNOSE="${ROOT}/scripts/diagnose_robot_visible_rigid_tool_baseline.py"
RESULT_ROOT="${NEWTON_ROOT}/phystwin_bridge/results/robot_visible_rigid_tool_baseline"
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
  --tabletop-control-mode joint_trajectory
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
  --particle-radius-scale 0.1
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
  --rope-line-width 0.006
  --visible-tool-mode short_rod
  --visible-tool-body right_finger
  --visible-tool-radius 0.0055
  --visible-tool-half-height 0.0100
  --visible-tool-offset 0.0 0.0105 0.0605
  --visible-tool-axis z
  "$@"
)

PRESENT_CMD=(
  python "${SCRIPT}"
  --out-dir "${PRESENT_DIR}"
  --prefix robot_visible_tool_tabletop_hero
  --render-mode presentation
  --camera-profile hero
  "${COMMON_ARGS[@]}"
)

DEBUG_CMD=(
  python "${SCRIPT}"
  --out-dir "${DEBUG_DIR}"
  --prefix robot_visible_tool_tabletop_hero_debug
  --render-mode debug
  --camera-profile hero
  --overlay-label
  "${COMMON_ARGS[@]}"
)

VALIDATION_CMD=(
  python "${SCRIPT}"
  --out-dir "${VALIDATION_DIR}"
  --prefix robot_visible_tool_tabletop_hero_validation
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
  "presentation_ready": false,
  "tool_is_visible_throughout_interaction": false,
  "visible_tool_is_actual_physical_contactor": false,
  "visible_tool_geometry_matches_actual_collider": false,
  "rope_render_thickness_matches_physical_contact_thickness": false,
  "no_hidden_helper": false,
  "no_multi_frame_visible_standoff_gap": false,
  "no_fake_geometry_appearance": false
}
EOF

{
  echo "[run_robot_visible_rigid_tool_baseline] run_dir=${RUN_DIR}"
  echo "[run_robot_visible_rigid_tool_baseline] presentation=${PRESENT_CMD[*]}"
  echo "[run_robot_visible_rigid_tool_baseline] debug=${DEBUG_CMD[*]}"
  echo "[run_robot_visible_rigid_tool_baseline] validation=${VALIDATION_CMD[*]}"
} | tee "${STDOUT_LOG}"

"${PRESENT_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
"${DEBUG_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"
"${VALIDATION_CMD[@]}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"

cp -f "${PRESENT_DIR}/robot_visible_tool_tabletop_hero.mp4" "${RUN_DIR}/hero_presentation.mp4"
cp -f "${DEBUG_DIR}/robot_visible_tool_tabletop_hero_debug.mp4" "${RUN_DIR}/hero_debug.mp4"
cp -f "${VALIDATION_DIR}/robot_visible_tool_tabletop_hero_validation.mp4" "${RUN_DIR}/validation_camera.mp4"

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

VALIDATION_RC=0
python "${VALIDATOR}" "${RUN_DIR}" --manual-review-json "${MANUAL_REVIEW_JSON}" || VALIDATION_RC=$?
python "${DIAGNOSE}" "${RUN_DIR}" --out-dir "${DIAG_DIR}" >> "${STDOUT_LOG}" 2>> "${STDERR_LOG}"

for artifact in tool_geometry_report.md tool_vs_collider_report.md rope_visual_vs_physical_thickness_report.md multimodal_review.md tool_contact_onset_report.json tool_clearance_timeseries.csv rope_vs_tool_scale_summary.json hidden_helper_verdict.md; do
  if [[ -f "${DIAG_DIR}/${artifact}" ]]; then
    cp -f "${DIAG_DIR}/${artifact}" "${RUN_DIR}/${artifact}"
  fi
done

if [[ -f "${DIAG_DIR}/review_bundle_hero/event_sheet.png" ]]; then
  cp -f "${DIAG_DIR}/review_bundle_hero/event_sheet.png" "${RUN_DIR}/event_sheet.png"
fi

cat > "${RUN_DIR}/manifest.json" <<EOF
{
  "run_id": "${RUN_ID}",
  "task": "robot_visible_rigid_tool_baseline",
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
    "event_sheet": "event_sheet.png",
    "keyframes_dir": "keyframes/",
    "physics_validation_json": "physics_validation.json",
    "tool_geometry_report": "tool_geometry_report.md",
    "tool_vs_collider_report": "tool_vs_collider_report.md",
    "rope_visual_vs_physical_thickness_report": "rope_visual_vs_physical_thickness_report.md",
    "multimodal_review": "multimodal_review.md",
    "diagnostics_dir": "diagnostics/"
  }
}
EOF

echo
echo "Candidate run directory:"
echo "  ${RUN_DIR}"
echo "Key outputs:"
echo "  ${RUN_DIR}/hero_presentation.mp4"
echo "  ${RUN_DIR}/hero_debug.mp4"
echo "  ${RUN_DIR}/validation_camera.mp4"
echo "  ${RUN_DIR}/tool_geometry_report.md"
echo "  ${RUN_DIR}/tool_vs_collider_report.md"
echo "  ${RUN_DIR}/rope_visual_vs_physical_thickness_report.md"
echo "  ${RUN_DIR}/multimodal_review.md"
echo "Validator exit code:"
echo "  ${VALIDATION_RC}"
echo "Manual review template:"
echo "  ${MANUAL_REVIEW_JSON}"
