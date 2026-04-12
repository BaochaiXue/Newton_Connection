> status: active
> canonical_replacement: none
> owner_surface: `newton_robot_examples_kb_update`
> last_reviewed: `2026-04-11`
> review_interval: `14d`
> update_rule: `Update when the implementation steps for this doc-sync pass change materially.`
> notes: Runbook for promoting official Newton robot-example lessons into durable docs.

# Implement: newton_robot_examples_kb_update

## Inputs To Re-read First

- `docs/bridge/tasks/newton_robot_examples_kb_update.md`
- `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- `diagnostics/split_v3_native_demo_lessons.md`
- `diagnostics/native_newton_demo_lessons.md`

## Implementation Steps

1. Re-read the upstream examples under `Newton/newton/newton/examples/` and
   extract only durable, reusable patterns.
2. Write one long-lived page under `docs/newton/` that:
   - ranks the most relevant examples
   - explains what each one is actually good for
   - records the repo-specific caution about the retired robot-demo line
3. Update `docs/newton/README.md` so future readers can discover the page.
4. Add only minimal supporting updates to nearby Newton pages when the new page
   changes their meaning materially.
5. Update `tasks/status/newton_robot_examples_kb_update.md`.
6. Run `python scripts/lint_harness_consistency.py`.

## Validation Notes

- Prefer link/discoverability and conclusion clarity over broad doc churn.
- Do not duplicate the historical split-v3 diagnosis verbatim; compress it into
  durable guidance.
