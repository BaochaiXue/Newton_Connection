# Spec: harness_markdown_cleanup_20260401

> status: historical
> canonical_replacement: `tasks/spec/markdown_harness_maintenance_upgrade.md`
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> notes: Historical predecessor spec; do not update this file for current markdown truth work.

## Goal

Remove stale harness markdown and make the remaining harness docs accurately
describe the current repo-native workflow.

## Non-Goals

- Auditing third-party markdown under vendored or upstream subtrees
- Rewriting stable technical docs just for style
- Changing Newton core documentation under `Newton/newton/`

## Inputs

- `AGENTS.md`
- `docs/PROJECT_MAP.md`
- `docs/bridge/current_status.md`
- `docs/bridge/experiment_index.md`
- root legacy markdown files and duplicate bunny scaffold files

## Outputs

- cleaned markdown file set
- updated harness rules and project-map docs
- task-local status record for this cleanup

## Constraints

- Do not touch `Newton/newton/`
- Prefer deletion for truly orphaned / duplicated docs over keeping contradictory copies
- Keep the docs aligned with actual repo paths and bundle layouts

## Done When

- legacy singleton docs are gone
- duplicate bunny scaffold docs are gone
- authoritative harness docs explain the current canonical pattern
