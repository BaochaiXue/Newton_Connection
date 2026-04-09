> status: canonical
> canonical_replacement: none
> owner_surface: `robot_ps_interaction_retirement`
> last_reviewed: `2026-04-09`
> review_interval: `90d`
> update_rule: `Update only if the project explicitly reopens a new robot-deformable interaction line with a different claim boundary.`
> notes: Canonical retrospective and retirement decision for the bridge-side robot + deformable PS-object demo line.

# Decision: Retire The Current Robot + Deformable Demo Line

## Date

2026-04-09

## Status

Accepted

## Context

The project tried multiple robot + deformable demo branches:

- readable tabletop hero
- remote-interaction truth fix
- one-way SemiImplicit baseline
- visible rigid tool intermediary
- direct-finger physical blocking
- native-style v2 rewrite
- split-v3 robot-first architecture
- Stage-0 native blocking baselines

These branches produced interesting partial artifacts, but the final required
claim was stricter than any partial success:

1. the robot must stay upright and not visually collapse
2. the table must physically block the robot
3. the same robot path must also push the bridged deformable object in a
   readable, honest way

The current bridge-side robotics demos never produced one meeting-grade clip
that satisfied all three at the same time.

## Decision

Retire the current robot + deformable PS-object demo line as an active
workstream.

Actions:

- archive the robot demo task chains
- mark existing robot result surfaces as historical rather than promoted live
  truth
- remove bridge-side robot demo entrypoints and their dedicated wrappers /
  validators from the active repo surface
- preserve the strongest partial evidence only as historical context

## Lessons

### What Worked

- readable baselines were possible when the robot path was effectively
  kinematic or otherwise conservative
- stage-scoped diagnostics were useful:
  - rigid-only blocking
  - rope-integrated follow-ons
  - same-history rerender checks
- the official Newton path (`SolverMuJoCo` + `gravcomp`) was materially more
  stable than the old bridge-side `SolverSemiImplicit` articulation route

### Why We Still Failed

#### 1. Readability and physics truth diverged

The most readable clips came from controller semantics that suppressed robot
tracking error or weakened the physical claim. Those clips were useful as
baselines, but they did not prove real two-way robot-table-deformable
interaction.

#### 2. The honest direct-finger path exposed robot-side actuation weakness

Once the bridge stopped overwriting robot state and allowed solver-owned motion
to matter, the robot no longer stayed visually clean. The same change that
made table blocking honest also exposed sag, poor pre-contact posture, and
unclear mid-clip body configurations.

#### 3. Partial fixes solved different problems, not the final combined claim

- one-way baseline: readable rope push, but not physical table blocking
- visible-tool baseline: honest contactor, but not direct finger
- rigid-only blocking: real table contact, but no deformable object
- native-style MuJoCo source path: better robot stability, but still no final
  meeting-grade combined robot-table-rope story

#### 4. Camera repair could not replace mechanism repair

Repeated camera and presentation adjustments improved interpretability, but they
did not create a real combined success. A clip that requires camera tricks to
hide posture ambiguity is not a trustworthy final result surface.

#### 5. The project never reached a defensible final claim boundary

The branch produced useful mechanism studies and negative results, but it did
not produce the required final artifact. Keeping these surfaces promoted or
active would mislead future agents about what was actually achieved.

## Consequences

- all current bridge-side robot demos are treated as historical / retired
- existing robot result bundles remain useful only as archived evidence
- future work must explicitly reopen a new claim boundary instead of inheriting
  the old robotics surfaces by default
- harness surfaces must stop presenting robot demo lines as active or promoted

## Related Tasks / Plans

- `docs/archive/tasks/robot_deformable_demo.md`
- `docs/archive/tasks/robot_rope_franka_tabletop_push_hero.md`
- `docs/archive/tasks/robot_rope_franka_semiimplicit_oneway.md`
- `docs/archive/tasks/robot_visible_rigid_tool_baseline.md`
- `docs/archive/tasks/robot_rope_franka_physical_blocking.md`
- `docs/archive/tasks/native_robot_physical_blocking_minimal.md`
- `docs/archive/tasks/native_robot_rope_drop_release.md`
