# Harness Deprecations

Updated: 2026-04-01

This ledger records harness surfaces that are intentionally no longer
canonical.

## Root Singleton Task Docs

- Deprecated:
  - `Plan.md`
  - `Status.md`
  - `Prompt.md`
  - `DecisionLog.md`
- Canonical replacement:
  - `docs/bridge/tasks/<task>.md`
  - `tasks/spec/<task>.md`
  - `plans/active/<task>.md`
  - `tasks/implement/<task>.md`
  - `tasks/status/<task>.md`

## Self-Collision Slug Alias

- Deprecated slug family:
  - `self_collision_transfer_decision`
- Canonical slug:
  - `self_collision_transfer`
- Migration path:
  - keep `_decision` files as explicit deprecation pointers only

## Historical Self-Collision Campaign Surface

- Historical task family:
  - `final_self_collision_campaign`
- Canonical active task:
  - `self_collision_transfer`
- Migration path:
  - treat `final_self_collision_campaign` files as historical campaign records

## Local Result-Bundle Authority Surfaces

- Secondary/local-only:
  - bundle-local `BEST_RUN.md`
  - bundle-local `LATEST_SUCCESS.txt`
  - bundle-local `LATEST_ATTEMPT.txt`
  - bundle-local `INDEX.md`
- Canonical committed replacement:
  - `results_meta/tasks/*.json`
  - `results_meta/INDEX.md`
  - `results_meta/LATEST.md`
