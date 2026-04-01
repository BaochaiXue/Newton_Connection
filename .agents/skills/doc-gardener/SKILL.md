---
name: doc-gardener
description: Repair stale pointers, duplicate truth surfaces, deprecated-but-not-marked files, and portability drift in the repo docs/control plane.
---

# Doc Gardener

Use this skill when documentation drift or duplicate truth surfaces are slowing
agents down.

## Goal

Keep one canonical surface per concept and make deprecations explicit.

## Check For

- stale run pointers
- duplicate task slugs
- missing spec/plan/implement/status links
- absolute machine-local paths in durable docs
- deprecated files without migration notes
- overgrown dashboards that should be maps, not ledgers
- active-vs-historical task mixing
- local result surfaces that sound canonical without `results_meta/` backing
- stale review ages or missing metadata on high-value control-plane docs

## Standard Closeout

When this skill leads to edits, finish by:

1. running `python scripts/generate_md_inventory.py`
2. reviewing:
   - `docs/generated/md_orphans.md`
   - `docs/generated/md_deprecation_matrix.md`
   - `docs/generated/md_staleness_report.md`
   - `docs/generated/task_surface_matrix.md`
3. aligning `results_meta/` if promoted/current result meaning changed
4. rerunning `python scripts/lint_harness_consistency.py`
5. keeping `docs/bridge/current_status.md` short and dashboard-like

## Rule

If the same ambiguity appears twice, encode the fix into docs, lint, or hooks.
