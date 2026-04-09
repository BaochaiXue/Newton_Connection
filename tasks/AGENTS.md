# Tasks Subtree Rules

This subtree stores execution-facing control-plane artifacts.

## Canonical Rule

For an active task, prefer one canonical slug across:

- `docs/bridge/tasks/`
- `tasks/spec/`
- `tasks/implement/`
- `tasks/status/`
- `plans/active/`

When a task promotes or blocks a major local result bundle, update the matching
`results_meta/tasks/<task_slug>.json` entry as part of the same milestone.

## Deprecated Surfaces

Do not recreate retired root singleton docs such as `Plan.md` or `Status.md`.

When a task page or task-chain file becomes deprecated or historical, add a
top-of-file metadata block with:

- `status`
- `canonical_replacement`
- `owner_surface`
- `last_reviewed`
- `notes`

Then refresh `docs/generated/md_inventory.*` and rerun
`scripts/lint_harness_consistency.py`.

## Handoffs And Contracts

Use `tasks/contracts/` for milestone acceptance and `tasks/handoffs/` for
session-to-session resume state.

## User-Facing Reporting

Task status files may keep detailed commands and bookkeeping, but user-facing
updates should not mirror that raw log.

Canonical details live in [docs/runbooks/agent_reporting.md](../docs/runbooks/agent_reporting.md).

When reporting task progress or closeout, lead with:

1. what changed
2. what problem was solved or clarified
3. findings or conclusions
4. relevant GIF/video/result/artifact paths
5. next step

Keep inventory/lint/task-chain maintenance as one short closeout note unless
the user explicitly asks for the maintenance details.
