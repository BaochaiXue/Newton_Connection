# Spec: markdown_truthfulness_cleanup

## Goal

Make the repo's control-plane Markdown fail closed by eliminating ambiguous
truth surfaces and making canonical / deprecated / historical state explicit.

## Non-Goals

- Editing `Newton/newton/`
- Rewriting heavy local result bundles only for doc cleanup
- Reauthoring stable technical explanation pages that are not part of the
  control plane

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

- cleaned canonical Markdown surfaces
- explicit deprecated/historical markers where needed
- generated Markdown inventory / orphan / cleanup reports
- markdown-maintenance runbook
- stronger lint / hook checks for doc drift

## Constraints

- `Newton/newton/` remains read-only
- prefer stub / archive / pointer over silent deletion unless a file is truly
  redundant and unreferenced
- treat `results_meta/` as the committed authority for current run meaning

## Done When

- required generated inventory and cleanup artifacts exist and are current
- no retired root singleton doc survives as a substantive live surface
- active task chains are clean and unique
- canonical Markdown surfaces have no machine-local absolute paths
- deprecated/historical files are clearly marked
- lint catches future Markdown truth drift
