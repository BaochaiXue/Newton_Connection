# Implement: phystwin_local_harness_engineering

## Preconditions

- A local PhysTwin checkout exists at `PhysTwin/`
- A runnable conda environment is available for real execution
- The target cases are listed in a config CSV and exist under the input case root

## Canonical Commands

Inspect the wrapper:

```bash
scripts/run_phystwin_local_pipeline.sh --help
```

Dry-run a data-process command:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_harness_dry_run_20260427 \
  --dry-run
```

Run data process for a config:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_reprocess_20260427
```

Run the full local PhysTwin pipeline:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode full \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_full_20260427
```

## Step Sequence

1. Confirm the config and input case root exist
2. Use `--dry-run` to inspect the exact command and run directory
3. Launch `--mode data-process` when only raw-capture processing is needed
4. Launch `--mode full` only when optimization/training/inference/eval are
   intended
5. Record `summary.json`, `run.log`, stage logs, and archive paths in the
   relevant task status page

## Validation

- Static shell parse succeeds
- Help output succeeds without requiring a pipeline run
- Dry-run creates:
  - `command.sh`
  - `summary.json`
- Real data-process runs should confirm per-case:
  - `mask/`
  - `pcd/`
  - `track_process_data.pkl`
  - `final_data.pkl`
  - `split.json`

## Output Paths

- Harness run root:
  - `PhysTwin/logs/harness_runs/<task_name>/`
- Full pipeline archive:
  - `PhysTwin/archive_result/<task_name>/`
