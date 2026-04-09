> status: canonical
> canonical_replacement: none
> owner_surface: `task_execution`
> last_reviewed: `2026-04-09`
> review_interval: `14d`
> update_rule: `Update when execution-directory structure or active-vs-historical task policy changes.`
> notes: Execution-layer map for task artifacts. Active and historical task chains must not share the same neighborhood silently.

# Task Artifacts

This directory stores execution-facing task files that complement the richer
encyclopedia pages under `docs/bridge/tasks/`.

## Structure

- `spec/`
  - concise task specs
- `implement/`
  - execution runbooks
- `status/`
  - current task-local progress logs
- `history/`
  - completed, deprecated, or superseded execution-layer task artifacts

## Relationship To `docs/bridge/tasks/`

- `docs/bridge/tasks/` explains the task
- `tasks/spec/` defines the concrete execution target
- `tasks/implement/` explains how to execute it
- `tasks/status/` records local progress
- `tasks/history/` preserves non-active execution artifacts without letting them
  masquerade as current work
