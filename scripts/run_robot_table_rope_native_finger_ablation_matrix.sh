#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DEMO="${ROOT}/scripts/run_robot_table_rope_split_demo.sh"
RUN_CAPSULE="${ROOT}/scripts/run_robot_table_rigid_capsule_panda_sanity.sh"
VALIDATOR="${ROOT}/scripts/validate_experiment_artifacts.py"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${1:-${ROOT}/tmp/robot_table_rope_native_finger_ablation_${STAMP}}"
if [[ $# -gt 0 ]]; then
  shift
fi
EXTRA_ARGS=("$@")

# Comma-separated case ids. Default is the bounded mechanism matrix with the
# rank-1 native rigid capsule control before interpreting rope outcomes.
MATRIX_CASES="${MATRIX_CASES:-00,01,02,03a,03b,03c,04,06,07,08,09}"

mkdir -p "${OUT_ROOT}"
CASE_INDEX="${OUT_ROOT}/case_index.tsv"
printf 'case_id\trank\tname\tpurpose\n' > "${CASE_INDEX}"

BASE_ARGS=(
  --coupling-mode one_way
  --video-mode presentation_pick_place
  --motion-pattern grasp_lift_place
  --rope-rigid-contact-max 8192
  --rope-soft-contact-max 8192
  --no-presentation-grasp-assist
  --gripper-yaw 2.89159265359
  --presentation-gripper-geometry panda_fingers
  --presentation-table-edge-inset-y 0.10
  --presentation-edge-grasp-outset-y 0.025
  --presentation-approach-x-offset 0.120
  --presentation-grasp-x-offset 0.030
  --presentation-grasp-z-offset 0.000
  --presentation-grasp-z-clearance 0.006
  --presentation-grasp-opening 0.080
  --presentation-grasp-closed-opening 0.000
  --presentation-table-shape-contact-scale 8.0
  --presentation-place-y-offset 0.180
  --presentation-place-ground-clearance 0.006
  --presentation-retract-x-offset 0.120
  --presentation-retract-y-offset 0.240
  --presentation-retract-z-offset 0.000
  --presentation-release-seconds 0.9
  --presentation-opening-seconds 0.08
  --presentation-approach-seconds 0.04
  --presentation-lift-seconds 0.55
  --presentation-transfer-seconds 0.55
  --presentation-place-lower-seconds 0.55
  --presentation-tail-frames 20
  --finger-shape-contact-scale 1.6
  --finger-shape-contact-damping-multiplier 12.0
  --finger-shape-friction-multiplier 50.0
  --arm-joint-target-ke 2500.0
  --arm-joint-target-kd 300.0
  --arm-joint-effort-limit 250.0
  --finger-joint-target-ke 1500.0
  --finger-joint-target-kd 180.0
  --finger-joint-effort-limit 80.0
  --num-frames 0
)

VALIDATION_FIELDS=(
  strict_contact_only_pass
  grasp_assist_enabled
  presentation_gripper_geometry
  presentation_aux_panda_pad_geometry_enabled
  strict_require_native_panda_fingers
  rope_lift_height_m
  grasp_particle_lift_during_lift_transfer_m
  rope_render_matches_physics
  opposing_contact_normal_score
  finger_contact_impulse_sum_by_side
  upward_friction_margin_estimate
  same_grasp_particle_ids_sustained
  rope_table_contact_frames_lift_window
  peak_particle_speed_lift_window_mps
  visible_collision_shape_manifest
  same_history_multiview_hash
)

CAPSULE_BASE_ARGS=(
  --presentation-gripper-geometry panda_fingers
  --no-presentation-grasp-assist
  --gripper-yaw 3.14159265359
  --presentation-grasp-x-offset 0.030
  --presentation-grasp-y-offset 0.005
  --presentation-grasp-z-offset 0.000
  --presentation-grasp-z-clearance 0.000
  --presentation-grasp-opening 0.080
  --presentation-grasp-closed-opening 0.000
  --presentation-place-y-offset 0.180
  --presentation-place-ground-clearance 0.006
  --presentation-retract-x-offset 0.120
  --presentation-retract-y-offset 0.240
  --presentation-retract-z-offset 0.000
  --presentation-release-seconds 0.9
  --presentation-opening-seconds 0.08
  --presentation-approach-seconds 0.04
  --presentation-lift-seconds 0.55
  --presentation-transfer-seconds 0.55
  --presentation-place-lower-seconds 0.55
  --presentation-tail-frames 20
  --presentation-post-close-hold-seconds 0.30
  --presentation-preload-seconds 0.20
  --presentation-preload-height 0.006
  --arm-joint-target-ke 2500.0
  --arm-joint-target-kd 300.0
  --arm-joint-effort-limit 250.0
  --finger-joint-target-ke 1500.0
  --finger-joint-target-kd 180.0
  --finger-joint-effort-limit 80.0
  --num-frames 0
)

CAPSULE_VALIDATION_FIELDS=(
  diagnostic_kind
  strict_native_panda_fingers
  presentation_gripper_geometry
  uses_semiimplicit_rope
  uses_grasp_assist
  uses_rope_cradle
  uses_hidden_helper_geometry
  capsule_radius_m
  capsule_length_m
  capsule_mass_kg
  capsule_lift_height_m
  first_finger_capsule_contact_frame
  lift_window_both_finger_capsule_contact_frames
  lift_window_unilateral_finger_capsule_contact_frames
  capsule_table_contact_frames_lift_window
  capsule_table_contact_frames_after_actual_lift_begins
  capsule_peak_speed_mps
  max_capsule_height_guard_pass
  release_final_finger_capsule_contact_frames
  rigid_capsule_sanity_pass
  same_history_hash
  visible_collision_manifest
)

should_run() {
  local case_id="$1"
  [[ "${MATRIX_CASES}" == "all" || ",${MATRIX_CASES}," == *",${case_id},"* ]]
}

validate_case() {
  local out_dir="$1"
  local cmd=(python "${VALIDATOR}" "${out_dir}" --require-video --require-gif)
  for field in "${VALIDATION_FIELDS[@]}"; do
    cmd+=(--summary-field "${field}")
  done
  "${cmd[@]}" | tee "${out_dir}/validate.log"
}

validate_capsule_case() {
  local out_dir="$1"
  local cmd=(python "${VALIDATOR}" "${out_dir}" --require-video --require-gif)
  for field in "${CAPSULE_VALIDATION_FIELDS[@]}"; do
    cmd+=(--summary-field "${field}")
  done
  "${cmd[@]}" | tee "${out_dir}/validate.log"
}

run_case() {
  local case_id="$1"
  local rank="$2"
  local name="$3"
  local purpose="$4"
  shift 4
  if ! should_run "${case_id}"; then
    return 0
  fi
  local out_dir="${OUT_ROOT}/rank_${rank}_${name}"
  printf '%s\t%s\t%s\t%s\n' "${case_id}" "${rank}" "${name}" "${purpose}" >> "${CASE_INDEX}"
  bash "${RUN_DEMO}" "${out_dir}" "${BASE_ARGS[@]}" "$@" "${EXTRA_ARGS[@]}"
  validate_case "${out_dir}"
}

run_capsule_case() {
  local case_id="$1"
  local rank="$2"
  local name="$3"
  local purpose="$4"
  shift 4
  if ! should_run "${case_id}"; then
    return 0
  fi
  local out_dir="${OUT_ROOT}/rank_${rank}_${name}"
  printf '%s\t%s\t%s\t%s\n' "${case_id}" "${rank}" "${name}" "${purpose}" >> "${CASE_INDEX}"
  bash "${RUN_CAPSULE}" "${out_dir}" "${CAPSULE_BASE_ARGS[@]}" "$@" "${EXTRA_ARGS[@]}"
  validate_capsule_case "${out_dir}"
}

run_case 00 00 baseline_replay "Replay current native-Panda outside-tight setup with mechanism metrics."
run_capsule_case 01 01 native_rigid_capsule_sanity "Native Panda/table rigid capsule control for gripper geometry and trajectory."
run_case 02 02 overhang_20mm "Move grasp segment farther outside the table edge." \
  --presentation-edge-grasp-outset-y 0.020
run_case 03a 03 gap_2p4r "Approximate closed gap at 2.4 rope radii for normal-force scan." \
  --presentation-grasp-closed-opening 0.0125
run_case 03b 03 gap_2p0r "Approximate closed gap at 2.0 rope radii for normal-force scan." \
  --presentation-grasp-closed-opening 0.0104
run_case 03c 03 gap_1p7r "Approximate closed gap at 1.7 rope radii for normal-force scan." \
  --presentation-grasp-closed-opening 0.0088
run_case 04 04 close_hold_preload "Close, hold, tiny preload, then lift for contact stabilization." \
  --presentation-post-close-hold-seconds 0.30 \
  --presentation-preload-seconds 0.20 \
  --presentation-preload-height 0.006
run_case 06 06 friction_4x "Reduce to a 4x finger friction diagnostic while keeping mass fixed." \
  --finger-shape-friction-multiplier 4.0
run_case 07 07 contact_stiffness_damping "Moderate finger contact stiffness/damping scan point." \
  --finger-shape-contact-scale 2.4 \
  --finger-shape-contact-damping-multiplier 16.0
run_case 08 08 visible_panda_pads "Visible rubber pad diagnostic, not native-finger-only." \
  --presentation-gripper-geometry panda_pads \
  --no-strict-require-native-panda-fingers
run_case 09 09 radius_spacing "Small physical radius diagnostic without changing mass." \
  --particle-radius-scale 0.18

python - "${OUT_ROOT}" <<'PY'
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
index_path = root / "case_index.tsv"
rows = []
with index_path.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        summary_path = root / f"rank_{row['rank']}_{row['name']}" / "summary.json"
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        if payload.get("diagnostic_kind") == "native_rigid_capsule_sanity":
            rows.append(
                {
                    **row,
                    "case_kind": "native_rigid_capsule_sanity",
                    "summary": str(summary_path),
                    "smoke_only": payload.get("smoke_only"),
                    "physics_conclusion_allowed": payload.get("physics_conclusion_allowed"),
                    "rigid_capsule_sanity_pass": payload.get("rigid_capsule_sanity_pass"),
                    "rigid_capsule_sanity_gate_pass": payload.get("rigid_capsule_sanity_gate_pass"),
                    "rigid_capsule_sanity_fail_reasons": payload.get("rigid_capsule_sanity_fail_reasons"),
                    "capsule_lift_height_m": payload.get("capsule_lift_height_m"),
                    "lift_window_both_finger_capsule_contact_frames": payload.get(
                        "lift_window_both_finger_capsule_contact_frames"
                    ),
                    "lift_window_unilateral_finger_capsule_contact_frames": payload.get(
                        "lift_window_unilateral_finger_capsule_contact_frames"
                    ),
                    "capsule_table_contact_frames_lift_window": payload.get(
                        "capsule_table_contact_frames_lift_window"
                    ),
                    "capsule_table_contact_frames_after_actual_lift_begins": payload.get(
                        "capsule_table_contact_frames_after_actual_lift_begins"
                    ),
                    "capsule_peak_speed_mps": payload.get("capsule_peak_speed_mps"),
                    "visible_collision_manifest_hash": payload.get("visible_collision_manifest_hash"),
                    "same_history_hash": payload.get("same_history_hash"),
                }
            )
        else:
            rows.append(
                {
                    **row,
                    "case_kind": "native_rope_split",
                    "summary": str(summary_path),
                    "smoke_only": payload.get("smoke_only"),
                    "physics_conclusion_allowed": payload.get("physics_conclusion_allowed", True),
                    "strict_contact_only_pass": payload.get("strict_contact_only_pass"),
                    "strict_contact_only_fail_reasons": payload.get("strict_contact_only_fail_reasons"),
                    "rope_lift_height_m": payload.get("rope_lift_height_m"),
                    "grasp_particle_lift_during_lift_transfer_m": payload.get(
                        "grasp_particle_lift_during_lift_transfer_m"
                    ),
                    "lift_window_both_finger_rope_contact_frames": payload.get(
                        "lift_window_both_finger_rope_contact_frames"
                    ),
                    "opposing_contact_normal_score": payload.get("opposing_contact_normal_score"),
                    "finger_contact_impulse_sum_by_side": payload.get("finger_contact_impulse_sum_by_side"),
                    "upward_friction_margin_estimate": payload.get("upward_friction_margin_estimate"),
                    "same_grasp_particle_ids_sustained": payload.get("same_grasp_particle_ids_sustained"),
                    "rope_table_contact_frames_lift_window": payload.get("rope_table_contact_frames_lift_window"),
                    "peak_particle_speed_lift_window_mps": payload.get("peak_particle_speed_lift_window_mps"),
                    "visible_collision_shape_manifest_hash": payload.get("visible_collision_shape_manifest_hash"),
                    "same_history_multiview_hash": payload.get("same_history_multiview_hash"),
                }
            )

capsule_rows = [row for row in rows if row.get("case_kind") == "native_rigid_capsule_sanity"]
rope_rows = [row for row in rows if row.get("case_kind") == "native_rope_split"]
capsule_conclusive_rows = [row for row in capsule_rows if row.get("physics_conclusion_allowed") is True]
rope_conclusive_rows = [row for row in rope_rows if row.get("physics_conclusion_allowed") is not False]
capsule_pass = None if not capsule_conclusive_rows else bool(capsule_conclusive_rows[0].get("rigid_capsule_sanity_pass"))
rope_best_pass = None if not rope_conclusive_rows else bool(
    any(row.get("strict_contact_only_pass") is True for row in rope_conclusive_rows)
)
if capsule_rows and not capsule_conclusive_rows:
    interpretation = "rigid_capsule_sanity_smoke_only_no_physics_decision"
elif capsule_pass is None:
    interpretation = "rigid_capsule_sanity_pending"
elif rope_best_pass is None and capsule_pass:
    interpretation = "capsule_pass_native_rope_pending"
elif rope_best_pass is None:
    interpretation = "capsule_fail_native_rope_pending_implies_gripper_geometry_or_trajectory_likely"
elif not capsule_pass and not rope_best_pass:
    interpretation = "capsule_fail_rope_fail_implies_gripper_geometry_or_trajectory_likely"
elif capsule_pass and not rope_best_pass:
    interpretation = "capsule_pass_rope_fail_implies_rope_representation_or_split_contact_blocker"
elif capsule_pass and rope_best_pass:
    interpretation = "capsule_pass_rope_pass_promote_native_finger_candidate_for_audit"
else:
    interpretation = "capsule_fail_rope_pass_is_suspicious_audit_metrics_manifest_hash"

matrix = {
    "matrix": "robot_table_rope_native_finger_ablation",
    "root": str(root),
    "case_count": len(rows),
    "cases": rows,
    "matrix_decision": {
        "rigid_capsule_sanity_pass": capsule_pass,
        "native_rope_best_pass": rope_best_pass,
        "interpretation": interpretation,
    },
}
(root / "matrix_summary.json").write_text(json.dumps(matrix, indent=2), encoding="utf-8")
print(json.dumps(matrix, indent=2))
PY

printf '\nMatrix artifacts:\n'
printf '  Root: %s\n' "${OUT_ROOT}"
printf '  Case index: %s\n' "${CASE_INDEX}"
printf '  Matrix summary: %s\n' "${OUT_ROOT}/matrix_summary.json"
