> status: historical
> canonical_replacement: `../../../docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `robot_rope_franka_native_v2`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory spec archived out of `tasks/spec/`.

# Spec: robot_rope_franka_native_v2

## Goal

Create a new native-style bridge demo for Franka + table + rope that replaces
the old stronger-task execution path with:

- Cartesian EE waypoints
- native IK -> joint targets
- no joint-state overwrite
- truthful table blocking
- direct-finger rope interaction

## Scope

- Add a new standalone v2 demo under `Newton/phystwin_bridge/demos/`
- Add a new canonical wrapper under `scripts/`
- Reuse bridge helper functions when they help keep the demo small
- Keep the current physical-blocking diagnostics/validator working on v2 output
- Produce at least three v2 candidate bundles

## Non-Goals

- Modifying `Newton/newton/`
- Promoting a stronger authority file in this round
- Rewriting the accepted tabletop hero baseline
- Reusing visible tool or support-box crutches as the first v2 milestone

## Constraints

- Robot, table, and rope must stay native/bridge truthful
- Finger-box colliders remain the proof surface
- `joint_target_drive` semantics must be preserved
- `state_out.body_q` must remain the only post-step body truth
- Hero/debug/validation must come from one saved rollout history

## Inputs

- `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- `scripts/diagnose_robot_rope_physical_blocking.py`
- `scripts/validate_robot_rope_franka_physical_blocking.py`

## Outputs

- `demo_robot_rope_franka_native_v2.py`
- `run_robot_rope_franka_native_v2.sh`
- three v2 candidate bundles with same-history media
- updated task status and current-status docs

## Done When

- V2 no longer uses the old overwrite path
- Startup is visually clean
- Table physically blocks robot motion without tunneling
- Rope is visibly moved by direct-finger interaction
- At least one candidate is the strongest honest local result for this path
