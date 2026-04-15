# Spec: phystwin_four_new_cases_pipeline

## Goal

Ingest the four new PhysTwin raw-capture cases from
`PhysTwin/data_different_types_only.zip` into the canonical data directory and
run the full PhysTwin pipeline for only those four cases.

## Non-Goals

- Changing any Newton core code under `Newton/newton/`
- Running Newton bridge import/parity validation for these cases
- Reprocessing old PhysTwin cases outside the requested four-case subset

## Inputs

- `PhysTwin/data_different_types_only.zip`
- `PhysTwin/data/different_types/`
- `PhysTwin/pipeline_commnad.py`
- Per-stage pipeline scripts under `PhysTwin/`

## Outputs

- New raw case folders under `PhysTwin/data/different_types/`
- Four-case allowlist config for the pipeline
- Task-scoped logs under `PhysTwin/logs/`
- Archived render/eval outputs under `PhysTwin/archive_result/<task_name>/`
- Updated task docs under `docs/`, `plans/`, and `tasks/`

## Constraints

- `Newton/newton/` is read-only
- Delete the source zip only after a successful extraction
- Run the standard PhysTwin stage order
- Limit execution to:
  - `sloth_base_motion_ffs`
  - `sloth_base_motion_native`
  - `sloth_set_2_motion_ffs`
  - `sloth_set_2_motion_native`
- Treat the four new cases as `sloth,False` in the allowlist config unless
  runtime evidence shows otherwise

## Done When

- The four raw case folders are present in the canonical data root
- The zip file is removed
- The pipeline completes or stops with a concrete stage-level failure record
- Logs and output locations are written to the task status page
