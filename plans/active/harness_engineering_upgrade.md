# Plan: harness_engineering_upgrade

## Goal

Upgrade the repo harness so future Codex agents can execute long-running
physics, video, and presentation work with less drift and stronger evidence
discipline.

## Constraints

- No edits under `Newton/newton/`
- Preserve historical accepted evidence bundles
- Prefer explicit deprecation + migration over silent replacement

## Milestones

1. Audit the current harness, including docs, hooks, validators, results governance, and stale truth surfaces
2. Implement authoritative-chain cleanup, slug normalization, portable-path cleanup, and results metadata mirror
3. Add contracts, handoffs, skeptical video evaluator docs/prompts, harness lint, hook upgrades, and local AGENTS guidance
4. Validate the upgraded harness and record what changed plus what remains open

## Validation

- `docs/generated/harness_audit.md` exists and matches implemented changes
- `python scripts/lint_harness_consistency.py` runs
- docs cross-link correctly
- active tasks expose clean authoritative chains
- authoritative runs are legible from repo-only metadata

## Notes

- The initial audit should integrate the required specialist subagent findings before implementation.
