> status: historical
> canonical_replacement: `../../../docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `robot_rope_franka_native_v2`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory status log archived out of `tasks/status/`.

# Status: robot_rope_franka_native_v2

## Current State

- Historical
- New native-style v2 rewrite approved
- Old stronger-task path remains intact and non-authoritative
- v2 code path now exists and produces full same-history candidate bundles, but
  no candidate is yet promotable

## Last Completed Step

- Added the new Example-style bridge demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka_native_v2.py`
  - native-style scene/controller/simulation split
  - no pre/post joint-state overwrite in the simulation loop
  - same-history render path via saved rollout history
- Added the canonical wrapper:
  - `scripts/run_robot_rope_franka_native_v2.sh`
- Extended the existing blocking diagnose/validator path so v2 reports now
  include:
  - `frame0_table_overlap_detected`
  - `robot_table_first_contact_phase`
- Produced new v2 candidate bundles:
  - `20260408_082147_smoke`
  - `20260408_082413_safeprobe`
  - `20260408_082836_tuckedprobe`
  - `20260408_084315_smoke_v3`
  - `20260408_085234_smoke_v4`
  - `20260408_085602_highgain_v2`
  - `20260408_085945_armatureprobe`

## Latest Findings

- The v2 path **does** remove the old overwrite semantics:
  - Cartesian EE targets
  - Newton IK
  - `control.joint_target_pos`
  - solver-owned `state_out.body_q`
- The original v2 rough Cartesian targets were not actually reachable; they
  collapsed to nearly one pose under IK.
- A measured link7-to-gripper-center local offset (`~0.1654 m`) replaced the
  earlier hard-coded `0.22 m`, but that alone did not fix startup sag.
- The v2 phase generator now uses reachable seed poses derived from legacy
  joint-space references, so `PRE -> APPROACH -> CONTACT -> PUSH` is no longer
  geometrically degenerate.
- Even after the seed-based rewrite, the current bridge-side solver route still
  sags during `pre`:
  - `smoke_v4`: `robot_table_first_contact_phase = pre`
  - `highgain_v2`: `robot_table_first_contact_phase = pre`
  - `armatureprobe`: `robot_table_first_contact_phase = pre`
- Stronger gains and larger armature did not remove early `pre` contact.
- Rope motion remains negligible on these honest v2 candidates because the arm
  reaches the table-loading regime before a readable finger-to-rope push lands.

## Next Step

- Treat the current result as a real bridge-layer negative result:
  - the native-style rewrite is in place
  - the current bridge-side solver/actuation route still does not hold a clean
    direct-finger `PRE`
- Next bounded move:
  - compare this same v2 controller architecture against a minimal alternate
    solver path instead of further micro-tuning the same `SolverSemiImplicit`
    actuation surface
