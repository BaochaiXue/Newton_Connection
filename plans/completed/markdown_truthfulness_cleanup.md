# Plan: markdown_truthfulness_cleanup

## Goal

Harden the repo's Markdown control plane so a fresh agent can identify the
canonical truth surfaces without being misled by stale or conflicting docs.

## Constraints

- No edits under `Newton/newton/`
- Preserve historical value without letting historical files sound live
- Use `results_meta/` as the canonical committed result authority

## Milestones

1. Audit the Markdown control plane and classify every in-scope file
2. Create the cleanup task chain and generated inventory/report artifacts
3. Convert stale surfaces into explicit canonical / deprecated / historical
   states
4. Add or strengthen lint, runbook, and hook enforcement
5. Validate the cleaned control plane and update task status

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- generated inventory and cleanup docs match the filesystem state

## Notes

- One-off dated review/cleanup task chains may remain only as explicit
  historical records.
