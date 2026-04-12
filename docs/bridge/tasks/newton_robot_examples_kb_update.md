> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when official Newton robot-example conclusions are promoted into durable docs or when the bridge-side robot claim boundary changes.`
> notes: Canonical task page for promoting official Newton robot-example lessons from historical diagnostics into the long-lived repo knowledge base.

# Task: Newton Robot Examples KB Update

## Question

How should the repo store the reusable lessons from official Newton robot
examples so future agents do not have to reconstruct them from retired
split-v3 diagnostics or chat transcripts?

## Why It Matters

The project repeatedly reasons about:

- robot-first control ownership
- contact geometry fidelity at the fingers
- native table/world setup
- IK as online target generation
- split robot/deformable coupling

Those lessons currently exist mostly in historical diagnostics tied to the
retired robot + deformable line. They need a stable home under `docs/` that
preserves the current repo boundary:

- official examples remain useful mechanism references
- but the old bridge-side robot + deformable demo line is retired as active
  work

## Current Status

- Active
- Initial knowledge-promotion pass is in scope for this task
- The target durable landing zone is the `docs/newton/` encyclopedia layer

## Code Entry Points

- Main docs:
  - `docs/newton/README.md`
  - `docs/newton/architecture.md`
  - `docs/newton/runtime_and_contacts.md`
- Historical inputs:
  - `diagnostics/split_v3_native_demo_lessons.md`
  - `diagnostics/native_newton_demo_lessons.md`
  - `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- Upstream read-only sources:
  - `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
  - `Newton/newton/newton/examples/ik/example_ik_franka.py`
  - `Newton/newton/newton/examples/cloth/example_cloth_franka.py`
  - `Newton/newton/newton/examples/softbody/example_softbody_franka.py`
  - `Newton/newton/newton/examples/robot/example_robot_ur10.py`
  - `Newton/newton/newton/examples/robot/example_robot_policy.py`

## Canonical Commands

```bash
rg -n "robot_panda_hydro|ik_franka|cloth_franka|softbody_franka|robot_ur10|robot_policy" docs diagnostics Newton/newton/newton/examples -g '*.md'
python scripts/lint_harness_consistency.py
```

## Required Artifacts

- durable Newton knowledge page for official robot-example patterns
- task/spec/plan/implement/status surfaces for this doc-update pass
- updated `docs/newton/` entrypoints that link to the new page

## Success Criteria

- the reusable official-example lessons are stored under `docs/newton/`
- the doc explicitly records the current repo boundary:
  - `split_v3` is important historical mechanism work
  - the old robot + deformable demo line is still retired as active work
- future agents can find the page from `docs/newton/README.md`
- the task chain records what changed and how it was validated

## Open Questions

- Should future Newton example studies continue accumulating in the same
  `docs/newton/` page, or should they split by topic once the page grows?
- If robot + deformable work is reopened later, should that task cite this page
  directly as its required upstream-reading surface?

## Related Pages

- [docs/decisions/2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
- [docs/archive/tasks/robot_rope_franka_split_v3.md](../../archive/tasks/robot_rope_franka_split_v3.md)
