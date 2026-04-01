# Status: harness_engineering_upgrade

## Current State

Implemented for the current upgrade pass.

## Last Completed Step

Completed the main harness upgrade:

- added committed results metadata under `results_meta/`
- added skeptical video evaluator docs and scripts
- added harness lint and stronger hook enforcement
- normalized self-collision deprecation surfaces
- removed machine-local paths from durable harness docs and the root pipeline
  wrapper
- added repo-local skills and local `AGENTS.md` guidance for the upgraded
  control plane

## Next Step

Use the new steady-state workflow on future task promotions:

1. update the task status file
2. update `results_meta/tasks/<task_slug>.json`
3. run `python scripts/sync_results_registry.py`
4. run `python scripts/lint_harness_consistency.py`
5. for video tasks, prepare a skeptical review bundle and run the skeptical
   audit

## Blocking Issues

- None blocking this upgrade closeout
- Remaining tradeoffs:
  - local ignored bundle files under `results/` may still contain stale or
    machine-local wording, but they are now explicitly secondary surfaces
  - skeptical video `PASS` still requires a separate reviewer payload by design

## Artifact Paths

- `docs/generated/harness_audit.md`
- `docs/generated/harness_deprecations.md`
- `results_meta/`
- `docs/evals/`
- `scripts/sync_results_registry.py`
- `scripts/lint_harness_consistency.py`
