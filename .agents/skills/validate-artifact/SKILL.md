---
name: validate-artifact
description: Validate experiment and delivery artifact directories against the repo artifact contract. Use after running demos, diagnostics, profiling, or slide-generation workflows.
---

# Validate Artifact

## Goal

Turn “it probably worked” into an explicit artifact check.

## Main Tool

- `scripts/validate_experiment_artifacts.py`

## Use When

- an experiment directory was produced under `tmp/`
- a diagnostic bundle was written
- a pipeline claims to have generated summary/video/gif outputs

## Standard Checks

- README present
- command trace present
- summary present
- scene/rollout present
- diagnostic bundle present when expected

## Reporting Rule

If validation fails:

- do not say the task is done
- list the missing pieces explicitly
- update `tasks/status/<task>.md` with the failure
