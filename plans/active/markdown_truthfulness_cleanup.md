# Plan: markdown_truthfulness_cleanup

## Goal

Converge Markdown, filesystem state, and lint policy so the repo has one
fail-closed truth system instead of multiple plausible Markdown authorities.

## Constraints

- No edits under `Newton/newton/`
- No ambiguous live-looking duplicate Markdown surfaces
- Keep historical value, but make historical state explicit

## Milestones

1. Audit Markdown control-plane surfaces and classify them
2. Build repo-native generated inventory / orphan / deprecation artifacts
3. Deprecate, archive, merge, or delete misleading Markdown surfaces
4. Reconcile run-meaning claims against `results_meta/`
5. Strengthen lint/hooks/runbook coverage, then validate

## Validation

- `python scripts/lint_harness_consistency.py`
- Markdown inventory/report files refresh cleanly
- canonical status pages and `results_meta/` agree on authoritative runs

## Notes

- This task treats Markdown truthfulness as harness engineering, not cosmetic
  cleanup.
