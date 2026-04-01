# Spec: markdown_truthfulness_cleanup

## Goal

Make Markdown truth surfaces fail closed by inventorying control-plane docs,
normalizing canonical/deprecated/historical state, reconciling run authority
with `results_meta/`, and enforcing the policy mechanically.

## Non-Goals

- Editing `Newton/newton/`
- Rewriting heavy local result bundles only for documentation cleanup
- Preserving ambiguous historical files without an explicit status banner

## Inputs

- `AGENTS.md`
- `docs/README.md`
- `docs/bridge/current_status.md`
- `docs/generated/harness_audit.md`
- `docs/generated/harness_deprecations.md`
- `results_meta/README.md`
- `results_meta/INDEX.md`
- `results_meta/LATEST.md`
- `results_meta/DEPRECATED.md`
- `TODO.md`
- `docs/bridge/tasks/README.md`
- `tasks/AGENTS.md`
- `docs/bridge/tasks/AGENTS.md`
- `scripts/lint_harness_consistency.py`

## Outputs

- repo-native task chain for this cleanup
- generated Markdown inventory and cleanup reports
- canonical/archive/deprecated convergence for misleading Markdown surfaces
- stronger markdown drift checks in lint/hooks/runbooks

## Constraints

- Keep `Newton/newton/` read-only
- Prefer explicit deprecation/archive/pointer over silent deletion unless the
  file is trivial, reproducible, and unreferenced
- Treat `results_meta/` as the canonical committed source for run meaning

## Done When

- generated Markdown inventory/report artifacts exist and are current
- root retired singleton docs are absent or explicit stubs only
- `docs/bridge/current_status.md` and `results_meta/` agree on current
  authoritative runs
- no canonical Markdown surface contains machine-local absolute paths
- every active task has one clean truth chain
- lint passes with Markdown truthfulness checks enabled
