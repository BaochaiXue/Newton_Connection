# Implement: harness_markdown_cleanup_20260401

> status: historical
> canonical_replacement: `tasks/implement/markdown_truthfulness_cleanup.md`
> owner_surface: `markdown_truthfulness_cleanup`
> last_reviewed: `2026-04-01`
> notes: Historical predecessor runbook; kept only to preserve the earlier cleanup record.

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, and `TODO.md`
- Audit current harness markdown and reference usage

## Canonical Commands

```bash
rg --files -g '*.md'
rg -n 'Plan.md|Status.md|Prompt.md|DecisionLog.md' . -g '*.md' -g '*.py' -g '*.sh'
rg -n 'bunny_force_visualization_fullprocess|bunny_force_visualization_full_process' .
```

## Step Sequence

1. Confirm which harness markdown files are unreferenced or contradicted by newer docs
2. Delete duplicate / retired markdown files
3. Update the remaining harness docs to state the canonical task/plan/status workflow

## Validation

- no retained doc points to deleted harness files
- canonical bundle/index guidance matches the current repo

## Output Paths

- `AGENTS.md`
- `docs/PROJECT_MAP.md`
- `docs/bridge/current_status.md`
- `docs/bridge/experiment_index.md`
