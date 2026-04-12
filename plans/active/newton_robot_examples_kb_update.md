> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when milestones or validation expectations for this doc-sync pass change.`
> notes: Active plan for promoting official Newton robot-example lessons into durable repo docs.

# Plan: newton_robot_examples_kb_update

## Goal

Store the official Newton robot-example lessons in the long-lived knowledge
base instead of leaving them trapped in historical diagnostics or chat.

## Milestones

1. Create the task scaffold for this doc-update pass.
2. Add a durable `docs/newton/` page for official robot-example patterns.
3. Link the page from the `docs/newton/` entrypoints.
4. Record the change and the repo-boundary conclusion in `tasks/status/`.
5. Run a lightweight harness consistency check.

## Validation

- `python scripts/lint_harness_consistency.py`

## Notes

- The page should preserve a strict boundary:
  - official examples remain valuable references
  - the retired bridge-side robot + deformable line does not become active
    again by implication
