# Legacy Path Autopsy

Date: 2026-04-08

Scope:

- old robot + rope stronger-task path
- readable tabletop baseline used only as diagnosis context

## Legacy execution path summary

The legacy bridge path accumulated several incompatible robot semantics inside
one large demo:

- IK + direct state write
- `joint_trajectory` overwrite
- `joint_target_drive`
- replay / rerender side paths
- support-box add-ons
- visible-tool branches

That made it too easy to mistake:

- readable motion
- solver truth
- render truth
- physical blocking

for one another.

## What is reusable

Reusable only if re-certified:

- direct-finger proof surface:
  - actual imported multi-box finger colliders
- same-history hero/debug/validation render chain
- rope object-only bridge loading from PhysTwin IR
- artifact export and validator harness
- table/finger signed-distance diagnostics

## What is banned in the rewrite

Banned by default in the final execution path:

- old overwrite-based control logic
- `joint_trajectory` or any full joint path as body truth
- post-step `eval_fk(...)` from stale reduced state
- support-box-first design
- visible-tool-first design
- hidden helpers
- debug gizmo leakage into presentation
- old collapse metric as the final pass/fail mechanism

## Known failure modes of the legacy path

### 1. Fake stability by overwrite

The readable baseline looked stable because the robot state was effectively
imposed, not because the articulated system was physically holding itself up.

Physics consequence:

- contact-generated tracking error cannot persist
- a blocking table cannot really push the robot back if the state is imposed

### 2. Truthful mode exposes startup sag

Once the bridge switched to the truthful `joint_target_drive` path, the robot
could no longer hide articulation sag.

Observed consequence:

- startup or early-phase table loading appears before the intended contact phase

### 3. Support box as secondary complication

The support box was not the first cause of collapse.
It sometimes aggravated the visible failure, but the robot could already sag
into the table with support disabled.

### 4. Numeric metrics were not enough

Some runs looked numerically improved while still visually reading as
collapsed/resting.

Therefore:

- multimodal visual review must be the primary pass/fail surface

## Autopsy verdict

The old path is useful as a forensic record, not as the architecture to keep
patching.

The rewrite should preserve only:

- bridge-side rope loading
- same-history render/export
- direct-finger proof surfaces

Everything else should be treated as suspect until re-certified.
