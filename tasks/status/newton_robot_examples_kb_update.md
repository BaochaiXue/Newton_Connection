> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update after each meaningful knowledge-sync milestone and after validation.`
> notes: Live status log for the current official Newton robot-example knowledge-base update pass.

# Status: newton_robot_examples_kb_update

## Current State

- Active
- Initial knowledge-sync pass completed
- Durable `docs/newton/` landing page now exists
- Generated markdown control-plane surfaces are refreshed
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
- `cloth_franka` and `softbody_franka` are important split-coupling references,
  but they should not be over-claimed as proofs of the retired strict bridge
  demo boundary

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
