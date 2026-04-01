# Tasks Subtree Rules

This subtree stores execution-facing control-plane artifacts.

## Canonical Rule

For an active task, prefer one canonical slug across:

- `docs/bridge/tasks/`
- `tasks/spec/`
- `tasks/implement/`
- `tasks/status/`
- `plans/active/`

## Deprecated Surfaces

Do not recreate retired root singleton docs such as `Plan.md` or `Status.md`.

## Handoffs And Contracts

Use `tasks/contracts/` for milestone acceptance and `tasks/handoffs/` for
session-to-session resume state.
