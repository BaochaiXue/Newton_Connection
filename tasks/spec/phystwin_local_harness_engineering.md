# Spec: phystwin_local_harness_engineering

## Goal

Make local PhysTwin data-process and full-pipeline runs explainable and
reproducible from the repo root.

## Non-Goals

- Changing Newton core under `Newton/newton/`
- Rerunning the expensive PhysTwin pipeline as part of the scaffold change
- Replacing PhysTwin's internal stage scripts
- Reclassifying existing result archives as authoritative

## Inputs

- `PhysTwin/data/different_types/`
- PhysTwin case allowlist CSV files
- `PhysTwin/script_process_data.py`
- `PhysTwin/process_data.py`
- `PhysTwin/pipeline_commnad.py`

## Outputs

- A detailed data-process documentation page
- A top-level wrapper under `scripts/`
- A task page under `docs/bridge/tasks/`
- Matching spec, active plan, implementation runbook, and status log
- Updated navigation/status surfaces

## Constraints

- Preserve the existing PhysTwin stage order
- Keep generated run state under `PhysTwin/logs/harness_runs/<task_name>/`
- Do not treat a dry run as scientific validation
- Record real output paths in task status after any real pipeline execution

## Done When

- The wrapper passes static shell validation
- The wrapper `--help` path works
- A dry run writes command provenance and summary metadata
- Documentation explains inputs, stages, outputs, common failures, and bridge
  relevance
- The active task chain and status page are present
