# Task: Harness Markdown Cleanup 2026-04-01

> status: historical
> canonical_replacement: `docs/bridge/tasks/markdown_truthfulness_cleanup.md`
> owner_surface: `markdown_truthfulness_cleanup`
> last_reviewed: `2026-04-01`
> notes: Completed predecessor cleanup kept only as historical context for the broader markdown truthfulness pass.

## Question

Which harness and engineering markdown files in the repo are stale,
duplicated, or effectively garbage, and what is the minimum cleanup needed so
the markdown layer reflects the current repo-native workflow?

## Why It Matters

The repo now uses `AGENTS.md` + `docs/` + `plans/` + `tasks/` as the canonical
control plane. Legacy singleton markdown files and duplicate task scaffolds
create conflicting instructions for later agents.

## Current Status

- Completed
- Cleanup performed:
  - removed retired root singleton docs `Plan.md`, `Status.md`, `Prompt.md`,
    `DecisionLog.md`
  - removed duplicate bunny full-process scaffold files under `plans/active/`
    and `tasks/`
  - synchronized harness docs that still implied outdated control-plane or
    bundle-index conventions

## Code Entry Points

- Harness rules:
  - `AGENTS.md`
  - `docs/PROJECT_MAP.md`
- Status/index docs:
  - `docs/bridge/current_status.md`
  - `docs/bridge/experiment_index.md`
- Task scaffolding:
  - `plans/active/`
  - `tasks/spec/`
  - `tasks/implement/`
  - `tasks/status/`

## Canonical Commands

```bash
rg --files -g '*.md'
rg -n 'Plan.md|Status.md|Prompt.md|DecisionLog.md' . -g '*.md' -g '*.py' -g '*.sh'
rg -n 'bunny_force_visualization_fullprocess|bunny_force_visualization_full_process' .
```

## Required Artifacts

- cleaned harness markdown set
- removed legacy / duplicate markdown files
- updated authoritative harness docs explaining the canonical workflow

## Success Criteria

- no unreferenced root singleton task docs remain
- duplicate bunny full-process scaffold files are removed
- harness docs point agents to the current task/plan/status system
- status/index docs no longer teach stale bundle conventions

## Open Questions

- Should future harness maintenance live as a recurring task page, or stay as
  one-off cleanup entries like this?

## Related Pages

- [README.md](./README.md)
- [delivery_and_profiling_review_20260401.md](./delivery_and_profiling_review_20260401.md)
