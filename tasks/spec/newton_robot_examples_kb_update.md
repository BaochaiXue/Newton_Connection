> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the bounded scope or done criteria for the current robot-example knowledge sync changes.`
> notes: Execution spec for the current pass that promotes official Newton robot-example lessons into durable docs.

# Spec: newton_robot_examples_kb_update

## Goal

Promote the current understanding of official Newton robot examples from
historical diagnostics into the long-lived `docs/newton/` knowledge base.

## Non-Goals

- Editing `Newton/newton/`
- Reopening the retired bridge-side robot + deformable demo line
- Rewriting historical diagnostics as if they were still active execution truth

## Inputs

- `diagnostics/split_v3_native_demo_lessons.md`
- `diagnostics/native_newton_demo_lessons.md`
- `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- the read-only upstream examples under `Newton/newton/newton/examples/`

## Outputs

- `docs/newton/robot_example_patterns.md`
- linked updates in `docs/newton/README.md`
- small supporting updates in `docs/newton/architecture.md` and
  `docs/newton/runtime_and_contacts.md`
- aligned task/status surfaces for this documentation pass

## Constraints

- Keep `Newton/newton/` read-only
- Distinguish clearly between:
  - reusable upstream mechanism patterns
  - retired local robot-demo claims
- Prefer one durable knowledge page over multiple overlapping summary notes

## Done When

- the new durable page exists and is discoverable from `docs/newton/README.md`
- the page names the highest-signal examples and their correct scope
- the page warns against over-claiming what `cloth_franka` /
  `softbody_franka` prove
- the task status page records the updated conclusion and validation
