---
name: run-pipeline
description: Run a project pipeline or demo via canonical wrapper scripts, capture logs and commands, and summarize artifacts. Use when a task requires executing bridge scripts or generating deliverables.
---

# Run Pipeline

Use wrapper scripts under `scripts/` whenever they exist.

## Priority Order

1. Use a canonical wrapper from `scripts/`
2. If none exists, create one if the workflow is likely to repeat
3. Record the exact command and output paths

## Standard Expectations

- output directory is explicit
- `command.sh` is written
- `run.log` is written
- expected artifact paths are printed or documented

## Current Canonical Wrappers

- `scripts/run_bunny_force_diag.sh`
- `scripts/run_realtime_profile.sh`
- `scripts/run_robot_rope_franka.sh`
- `scripts/render_gif.sh`

## After Running

1. Inspect the output, do not assume success.
2. If the output is an experiment directory, run `scripts/validate_experiment_artifacts.py` when relevant.
3. Write artifact paths into `tasks/status/<task>.md`.
