# Plan: phystwin_local_harness_engineering

## Goal

Turn local PhysTwin data-process and pipeline execution into a repo-native
workflow with clear documentation, a canonical wrapper, and resumable task
state.

## Constraints

- Do not edit `Newton/newton/`
- Keep PhysTwin execution opt-in because the full pipeline is expensive
- Make the wrapper safe to inspect with `--help` and `--dry-run`
- Keep task-scoped run artifacts out of the repo root

## Milestones

1. Document the current PhysTwin data-process stage chain
2. Add a top-level wrapper for data-process-only and full-pipeline runs
3. Create the task/spec/plan/runbook/status chain
4. Update navigation surfaces so future agents find the wrapper first
5. Run lightweight validation and record results

## Validation

- `bash -n scripts/run_phystwin_local_pipeline.sh`
- `scripts/run_phystwin_local_pipeline.sh --help`
- `scripts/run_phystwin_local_pipeline.sh --mode data-process --task-name phystwin_harness_dry_run_20260427 --dry-run`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`

## Notes

- A real full-pipeline run should still be recorded in the relevant task status
  page with artifact paths under `PhysTwin/archive_result/<task_name>/`.
