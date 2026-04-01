# Plan: harness_engineering_upgrade

## Goal

Make the harness reliable enough that future agents can resume complex
physics/video/presentation work with less drift and fewer false positives.

## Constraints

- No edits under `Newton/newton/`
- Do not silently preserve competing truth surfaces
- Keep migrations explicit and discoverable

## Milestones

1. Audit the current harness and record exact failure modes
2. Repair source-of-truth drift across task/status/plan/result surfaces
3. Add results metadata mirrors, skeptical video evaluator assets, handoff/contracts, and lint/hook enforcement
4. Validate the upgraded harness and update task status/docs

## Validation

- `python scripts/lint_harness_consistency.py`
- cross-link checks over new docs and templates
- repo-only authoritative run discovery works for major tasks

## Notes

- This task is both a harness change and a harness self-test.
