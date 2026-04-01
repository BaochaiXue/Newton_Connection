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

- `scripts/run_bunny_force_diag.sh`
- `scripts/run_realtime_profile.sh`
- `scripts/run_robot_rope_franka.sh`
- `scripts/render_gif.sh`

## After Running

Run artifact validation when relevant and write the result to the task status log.
