# Status: PhysTwin Local Harness Engineering

## Current State

- Scaffold complete; no real PhysTwin processing run launched
- The local PhysTwin data-process flow has been documented in:
  - `docs/phystwin/data_process_flow.md`
- A repo-level wrapper now exists at:
  - `scripts/run_phystwin_local_pipeline.sh`
- The wrapper supports:
  - `--mode data-process`
  - `--mode full`
  - `--dry-run`
  - task-scoped `command.sh`
  - task-scoped `run.log`
  - task-scoped `summary.json`
- Lightweight validation passed:
  - `bash -n scripts/run_phystwin_local_pipeline.sh`
  - `scripts/run_phystwin_local_pipeline.sh --help`
  - `scripts/run_phystwin_local_pipeline.sh --mode data-process --config-path PhysTwin/configs/data_config_four_new_cases.csv --task-name phystwin_harness_dry_run_20260427 --dry-run`
  - `scripts/run_phystwin_local_pipeline.sh --mode full --config-path PhysTwin/configs/data_config_four_new_cases.csv --task-name phystwin_harness_full_dry_run_20260427 --dry-run`
- Generated markdown inventory was refreshed with:
  - `python scripts/generate_md_inventory.py`
- Harness consistency lint was run and failed on pre-existing control-plane
  hygiene issues outside this new wrapper chain:
  - `docs/bridge/current_status.md` is over the dashboard length limit
  - existing active pages `phystwin_four_new_cases_pipeline` and
    `phystwin_upstream_sync_review` lack standard task-page metadata
  - several existing active task surfaces have due review metadata

## Last Completed Step

- Created the task/spec/plan/runbook/status chain
- Added the local pipeline wrapper
- Added detailed stage documentation for PhysTwin data processing
- Ran the dry-run harness probe, which wrote command provenance without
  launching PhysTwin processing
- Ran a full-pipeline dry-run probe, which wrote the expected
  `pipeline_commnad.py` command and stage-log location without launching the
  pipeline
- Refreshed generated markdown inventory and recorded the residual lint
  failures

## Next Step

- Use the wrapper for the next real PhysTwin data-process or full-pipeline run
  and record real artifact paths here
- Separately decide whether to clean up the broader stale review metadata and
  overgrown dashboard lint failures

## Blocking Issues

- No current blocker for the wrapper/documentation scaffold
- Real PhysTwin execution is intentionally deferred because it can launch the
  expensive GPU data-processing or full training/evaluation stack
- Full harness lint remains blocked by existing metadata/dashboard debt outside
  the new PhysTwin local wrapper work

## Artifact Paths

- Wrapper:
  - `scripts/run_phystwin_local_pipeline.sh`
- Data-process docs:
  - `docs/phystwin/data_process_flow.md`
- Dry-run harness output:
  - `PhysTwin/logs/harness_runs/phystwin_harness_dry_run_20260427/`
  - `PhysTwin/logs/harness_runs/phystwin_harness_dry_run_20260427/command.sh`
  - `PhysTwin/logs/harness_runs/phystwin_harness_dry_run_20260427/summary.json`
- Full-mode dry-run harness output:
  - `PhysTwin/logs/harness_runs/phystwin_harness_full_dry_run_20260427/`
  - `PhysTwin/logs/harness_runs/phystwin_harness_full_dry_run_20260427/command.sh`
  - `PhysTwin/logs/harness_runs/phystwin_harness_full_dry_run_20260427/summary.json`
