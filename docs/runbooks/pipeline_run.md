# Pipeline Run Runbook

## Purpose

Describe the expected behavior of canonical pipeline/demo wrapper scripts.

## Wrapper Principles

Each wrapper should:

- create a clear output directory
- write `command.sh`
- write `run.log`
- print expected artifact paths at the end

## Current Wrappers

- `scripts/run_phystwin_local_pipeline.sh`
- `scripts/run_bunny_force_diag.sh`
- `scripts/run_realtime_profile.sh`
- `scripts/run_robot_rope_franka.sh`
- `scripts/render_gif.sh`

## PhysTwin Local Runs

Use the repo-level wrapper instead of launching PhysTwin internals directly
when a run should be reproducible from the workspace root:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode data-process \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_reprocess_20260427
```

For full PhysTwin processing/training/inference/evaluation:

```bash
scripts/run_phystwin_local_pipeline.sh \
  --mode full \
  --config-path PhysTwin/configs/data_config_four_new_cases.csv \
  --task-name phystwin_four_cases_full_20260427
```

The detailed stage contract is documented in
`docs/phystwin/data_process_flow.md`.

## After Running

Run artifact validation when relevant and write the result to the task status log.
