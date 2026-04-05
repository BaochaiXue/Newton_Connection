# Status: robot_rope_franka_physical_blocking

## Current State

- Active
- This is a new stronger task, separate from the accepted tabletop-push
  baseline
- Current state is now: `re-opened; the old bridge-layer limit proof is no
  longer sufficient after identifying stale post-step FK overwrite plus
  destabilizing default attachment gains in the joint_target_drive path`

## Last Completed Step

- Created the new stronger task chain.
- Completed the first control/contact diagnosis pass and added:
  - [control_update_order_report.md](/home/xinjie/Newton_Connection/diagnostics/control_update_order_report.md)
  - [control_timeline.md](/home/xinjie/Newton_Connection/diagnostics/control_timeline.md)
  - [suspected_kinematic_override.md](/home/xinjie/Newton_Connection/diagnostics/suspected_kinematic_override.md)
  - [pre_fix_multimodal_review.md](/home/xinjie/Newton_Connection/diagnostics/pre_fix_multimodal_review.md)
  - [root_cause_ranked_report.md](/home/xinjie/Newton_Connection/diagnostics/root_cause_ranked_report.md)
- Added new stronger-task tooling:
  - [diagnose_robot_rope_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/diagnose_robot_rope_physical_blocking.py)
  - [validate_robot_rope_franka_physical_blocking.py](/home/xinjie/Newton_Connection/scripts/validate_robot_rope_franka_physical_blocking.py)
  - [run_robot_rope_franka_physical_blocking.sh](/home/xinjie/Newton_Connection/scripts/run_robot_rope_franka_physical_blocking.sh)
- Added explicit limit-proof surfaces:
  - [bridge_layer_limit_proof.md](/home/xinjie/Newton_Connection/diagnostics/bridge_layer_limit_proof.md)
  - [minimal_core_change_proposal.md](/home/xinjie/Newton_Connection/diagnostics/minimal_core_change_proposal.md)

## Latest Findings

- The current promoted tabletop hero remains a readable baseline only
- The current tabletop `joint_trajectory` path in
  `demo_robot_rope_franka.py` directly assigns `state_in.joint_q/joint_qd`
  before the solver and writes `state_out.joint_q/joint_qd` back to the target
  after the solver
- This strongly suggests contact reaction cannot persist as tracking error under
  the current path
- Strongest current numerical proof:
  - [BEST_RUN blocking diagnostic](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/diagnostics_blocking/robot_table_contact_report.json)
    shows the accepted baseline never meaningfully contacts the table:
    - `robot_table_first_contact_time_s = null`
    - minimum finger-table clearance stays positive at about `+0.0288 m`
  - [c19 blocking diagnostic](/home/xinjie/Newton_Connection/diagnostics/physical_blocking_c19/robot_table_contact_report.json)
    shows the stronger true-size candidate reaches the table but still behaves
    kinematically:
    - `robot_table_penetration_min_m = -0.037999`
    - `ee_target_to_actual_error_during_block_mean_m = 2.5e-6`
- First bridge-layer physically actuated mode is now implemented:
  - `--tabletop-control-mode joint_target_drive`
  - desired joints are written into `model.control().joint_target_pos`
    instead of being forced into `state_in/state_out`
- Bridge/demo-level actuation attempts have now been exhausted far enough to
  change the task state:
  - early drive attempts (`c01/c02`) became numerically unstable
  - lower-gain retries (`c03/c04/c05`) stabilized numerically but still showed
    no rope contact and effectively no articulated reach into the rope-contact
    line
  - isolated control-surface smokes using:
    - `control.joint_target_pos`
    - `model.joint_target_pos`
    - `control.joint_f`
    all left `joint_q` unchanged in the current accessible bridge/demo path
- Current interpretation:
  - the old overwrite path is definitively non-physical
  - but the previous bridge-layer limit proof is now incomplete:
    - `joint_target_drive` used to re-run `eval_fk(state_out.joint_q, ...)`
      after `solver.step(...)`, which overwrote solver-integrated body motion
      with stale reduced coordinates
    - current local control smokes show `SolverSemiImplicit` articulation
      targets can remain stable for simple revolute and pure-robot Franka cases
      once `joint_attach_ke/kd` are reduced to a non-explosive regime such as
      roughly `50 / 5`
  - the task therefore moves back from “bridge-layer impossible” to
    “bridge-layer stronger benchmark still unproven, but no core change is
    justified yet”

## Next Step

- Build the simpler Stage-0 rigid-only blocking benchmark before touching the
  rope again.
- Keep `joint_target_drive` on the repaired bridge-layer path:
  - no post-step FK overwrite
  - explicit reduced-state resync through `eval_ik`
  - lowered attachment gains
- Only if Stage 0 still fails honestly after that should the task return to the
  minimal core/API proposal in
  [minimal_core_change_proposal.md](/home/xinjie/Newton_Connection/diagnostics/minimal_core_change_proposal.md).
- Keep the stronger-task docs truthful and preserve the old readable tabletop
  baseline as the only accepted robot-rope authority for now.

## Authority Rule

- Do not modify `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  from this task
- Only add `results_meta/tasks/robot_rope_franka_physical_blocking.json` after
  a real stronger-task pass
