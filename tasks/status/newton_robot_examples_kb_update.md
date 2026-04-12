> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-12`
> review_interval: `7d`
> update_rule: `Update after each meaningful knowledge-sync milestone and after validation.`
> notes: Live status log for the current official Newton robot-example knowledge-base update pass.

# Status: newton_robot_examples_kb_update

## Current State

- Active
- Initial knowledge-sync pass completed
- Durable `docs/newton/` landing page now exists
- Generated markdown control-plane surfaces are refreshed
- Native robot-driving families are now written explicitly
- Harness consistency lint passes

## What Changed In The Latest Pass

- Created the canonical task chain for this knowledge-sync work:
  - `docs/bridge/tasks/newton_robot_examples_kb_update.md`
  - `tasks/spec/newton_robot_examples_kb_update.md`
  - `plans/active/newton_robot_examples_kb_update.md`
  - `tasks/implement/newton_robot_examples_kb_update.md`
  - `tasks/status/newton_robot_examples_kb_update.md`
- Added the durable knowledge page:
  - `docs/newton/robot_example_patterns.md`
- Linked the page from:
  - `docs/newton/README.md`
  - `docs/newton/architecture.md`
  - `docs/newton/runtime_and_contacts.md`
- Added the task to the active bridge task index:
  - `docs/bridge/tasks/README.md`
- Tightened the page so it now states explicitly how current native demos drive
  robots:
  - `ik_franka` as IK-only reference generation
  - `robot_panda_hydro` / `robot_ur10` / `robot_policy` as
    `control.joint_target_pos`-driven rigid execution
  - `cloth_franka` / `softbody_franka` as staged robot/deformable coupling
- Explicitly downgraded archived local bridge robot practices to historical
  failure-analysis surfaces rather than recommended implementation templates

## Problem Being Solved

- official Newton robot-example lessons currently live mostly in historical
  split-v3 diagnostics instead of the durable knowledge base

## Findings / Conclusions So Far

- the long-lived landing zone should be `docs/newton/`, not another
  bridge-specific scratch note
- the durable doc must keep two statements true at once:
  - official examples remain valuable mechanism references
  - the old robot + deformable demo line is still retired as active work
- `robot_panda_hydro` is the highest-signal robot-side manipulation template
- `ik_franka` is best treated as online target generation
- current Newton native robot demos do not share one single solver family:
  - IK demos use `IKSolver`
  - rigid manipulation demos mainly drive through `control.joint_target_pos`
    plus rigid-body solvers
  - deformable demos stage robot motion separately before VBD stepping
- `cloth_franka` and `softbody_franka` are important split-coupling references,
  but they should not be over-claimed as proofs of the retired strict bridge
  demo boundary
- old local bridge robot practices are not worthwhile positive reference points
  anymore; they remain useful only as failure analyses

## Artifact Paths To Review

- `docs/newton/robot_example_patterns.md`
- `docs/bridge/tasks/newton_robot_examples_kb_update.md`
- `docs/generated/task_surface_matrix.md`

## Next Step

- if robot + deformable work is reopened later, use
  `docs/newton/robot_example_patterns.md` as the upstream-reading entrypoint
- promote future official-example studies into `docs/newton/` instead of
  leaving them in historical diagnostics only

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- current result after this pass: `PASS`
