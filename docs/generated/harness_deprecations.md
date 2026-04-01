# Harness Deprecations

> status: generated
> canonical_replacement: `docs/generated/md_deprecation_matrix.md`
> owner_surface: `markdown_truthfulness_cleanup`
> last_reviewed: `2026-04-01`
> notes: Generated deprecation ledger for harness/control-plane surfaces. Regenerate rather than treating this as a free-form scratchpad.

Updated: 2026-04-01

This ledger records harness surfaces that are intentionally no longer
canonical.

## Root Singleton Task Docs

- Retired and currently absent from the repo root:
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
- Migration rule:
  - do not recreate these files
  - if a discoverability stub is ever needed, it must be an explicit deprecated
    pointer and must not carry standalone current state

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

## Historical One-Off Cleanup / Review Tasks

- Historical task families:
  - `harness_markdown_cleanup_20260401`
  - `delivery_and_profiling_review_20260401`
- Canonical replacement:
  - `markdown_truthfulness_cleanup` for the broader markdown cleanup line
  - none for the completed one-off review
- Migration path:
  - keep these files only as historical records with explicit metadata blocks

## Deprecated Subtree Status Surface

- Deprecated file:
  - `Newton/phystwin_bridge/STATUS.md`
- Canonical replacement:
  - `docs/bridge/current_status.md`
- Migration path:
  - keep it only as an explicit pointer stub for subtree entry

## Historical One-Off Review / Cleanup Surfaces

- Historical task families:
  - `delivery_and_profiling_review_20260401`
  - `harness_markdown_cleanup_20260401`
- Canonical replacement:
  - `delivery_and_profiling_review_20260401`: none; keep as a historical review record only
  - `harness_markdown_cleanup_20260401`: `markdown_truthfulness_cleanup`
- Migration path:
  - move completed plans to `plans/completed/`
  - keep any remaining task/spec/implement/status files only with explicit `status: historical` metadata blocks

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
