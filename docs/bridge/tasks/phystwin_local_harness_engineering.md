> status: active
> canonical_replacement: none
> owner_surface: `phystwin_local_harness_engineering`
> last_reviewed: `2026-04-27`
> review_interval: `14d`
> update_rule: `Update when PhysTwin local pipeline wrappers, data-process stage contracts, or local run artifact expectations change.`
> notes: Canonical task page for making local PhysTwin runs reproducible through repo-native wrappers and status surfaces.

# Task: PhysTwin Local Harness Engineering

## Question

How should local PhysTwin data-process and full-pipeline runs be explained,
launched, logged, and resumed so they fit the repo-native harness instead of
depending on ad hoc commands?

## Why It Matters

PhysTwin is the upstream source of the deformable-object data that the bridge
later imports into Newton. If local PhysTwin runs do not have stable entry
points, stage-level logs, and task/status records, downstream bridge debugging
starts from uncertain data provenance.

## Current Status

- In progress
- The detailed data-process explanation now lives in
  `docs/phystwin/data_process_flow.md`
- The canonical local wrapper is:
  `scripts/run_phystwin_local_pipeline.sh`
- The wrapper supports:
  - data-process-only runs
  - full PhysTwin pipeline runs
  - task-scoped `command.sh`, `run.log`, and `summary.json`
  - full-pipeline stage logs under `stage_logs/`

## Code Entry Points

- Main wrapper:
  - `scripts/run_phystwin_local_pipeline.sh`
- PhysTwin batch/process entry points:
  - `PhysTwin/script_process_data.py`
  - `PhysTwin/process_data.py`
  - `PhysTwin/pipeline_commnad.py`
- Supporting utilities:
  - `scripts/clean_phystwin_case_outputs.py`
  - `scripts/fix_phystwin_calibrate_order.py`
- Relevant docs:
  - `docs/phystwin/data_process_flow.md`
  - `docs/phystwin/artifacts.md`
  - `docs/runbooks/pipeline_run.md`

## Canonical Commands

Data-process-only:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_reprocess_20260427
```

Full PhysTwin pipeline:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode full \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_full_20260427
```

Dry-run command generation:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_dry_run_probe \
  --dry-run
```

## Required Artifacts

- summary:
  - `PhysTwin/logs/harness_runs/<task_name>/summary.json`
- command provenance:
  - `PhysTwin/logs/harness_runs/<task_name>/command.sh`
  - `PhysTwin/logs/harness_runs/<task_name>/run.log`
- full-pipeline archive:
  - `PhysTwin/archive_result/<task_name>/`
- diagnostic outputs if applicable:
  - `PhysTwin/logs/harness_runs/<task_name>/stage_logs/`

## Success Criteria

- A new reader can understand the data-process stage without opening every
  PhysTwin script first
- Local runs have a repo-level wrapper under `scripts/`
- The wrapper can show help and dry-run without launching a GPU pipeline
- Task/spec/plan/runbook/status surfaces exist and link the workflow together
- The status page records validation and any run artifacts before claiming a
  real data-process or full-pipeline run as done

## Open Questions

- Should full PhysTwin runs gain an explicit `--end-stage` option upstream so
  partial stage windows do not require separate wrappers?
- Should `summary.json` eventually include per-case completion status parsed
  from stage logs?

## Related Pages

- `tasks/spec/phystwin_local_harness_engineering.md`
- `plans/active/phystwin_local_harness_engineering.md`
- `tasks/implement/phystwin_local_harness_engineering.md`
- `tasks/status/phystwin_local_harness_engineering.md`
