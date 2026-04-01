# Scripts Subtree Rules

This subtree contains canonical wrappers and utility scripts.

## Goal

Make repeatable workflows easier for Codex and humans.

## Script Expectations

Prefer wrappers that:

- create explicit output directories
- write `command.sh`
- write `run.log`
- print artifact locations
- point the user to results metadata updates when they promote authoritative runs
- point the user to skeptical video audit when they produce meeting-facing media

## Rule

If a command will likely be run repeatedly, prefer adding or updating a wrapper
script instead of retyping the long command in chat.

## Harness Upgrade Surfaces

High-signal harness scripts now also include:

- `scripts/sync_results_registry.py`
- `scripts/lint_harness_consistency.py`
- `scripts/prepare_video_review_bundle.py`
- `scripts/run_skeptical_video_audit.py`
