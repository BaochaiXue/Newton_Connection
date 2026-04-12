> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-12`
> review_interval: `14d`
> update_rule: `Update when progressive-disclosure policy, root hygiene, bundle-entry quarantine, hook semantics, inventory generation, or lint policy changes.`
> notes: Current canonical harness-maintenance task for markdown truthfulness, active-vs-historical separation, root hygiene, registry-backed result authority, and outcome-first agent reporting.

# Task: Markdown Harness Maintenance Upgrade

## Question

How do we tighten the existing harness so Markdown truth surfaces stay
fail-closed, active entrypoints stay map-like, root-level clutter stops
competing with canonical navigation, and committed result authority remains
legible without trusting local bundle pointers?

## Why It Matters

This repo already has a real harness. The remaining risk is not missing
structure; it is semantic drift:

- dashboards growing into ledgers
- active indexes enumerating history instead of routing to archive hubs
- root-level reusable tools/configs competing with repo entry surfaces
- hooks blocking read-only inspection because path names look scary
- historical files living beside active task chains
- local bundle READMEs sounding canonical
- retired local mechanism practices continuing to sound like recommended
  implementation references
- inventory/lint scripts detecting presence but missing stale meaning or root clutter

## Current Scope

- markdown truthfulness and stale-doc garbage collection
- progressive disclosure for live entrypoints
- active-vs-historical task separation
- root-level allowlist policy for tracked files
- `results_meta/` completeness and local-only pointer hygiene
- deep-bundle quarantine: index only approved entry surfaces under `results/` and `Newton/phystwin_bridge/results/`
- family-root-only Markdown browsing surfaces under `results/`, with deeper
  local notes demoted to `.txt`
- downgrade stale mechanism guidance that still points at retired robot
  practices instead of current Newton native patterns
- markdown inventory / staleness / task-surface generation
- lint / hook reinforcement for ongoing maintenance, including write-strict/read-loose behavior
- outcome-first user-facing reporting discipline for future Codex runs

## Canonical Entry Points

- `docs/bridge/current_status.md`
- `docs/bridge/tasks/README.md`
- `docs/archive/tasks/README.md`
- `tasks/README.md`
- `results_meta/README.md`
- `docs/runbooks/doc_gardening.md`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`

## Required Outputs

- refreshed markdown inventory surfaces under `docs/generated/`
- new `md_staleness_report.md`
- new `task_surface_matrix.md`
- current-status dashboard trim / reroute
- archive-hub routing from active entrypoints
- root-level tracked-file cleanup and allowlist policy
- family-root-only local browsing entry surfaces under `results/`
- active-vs-historical execution-directory cleanup
- stronger markdown maintenance policy and enforcement
- durable reporting contract in repo instructions and hooks so chat summaries stay focused on outcomes

## Success Criteria

- one active harness-maintenance task chain exists for the current pass
- active entrypoints route through maps and archive hubs instead of inline historical lists
- tracked root files outside the allowlist are moved, ignored, or explicitly justified
- completed predecessor harness tasks no longer sit in active execution dirs
- `docs/bridge/current_status.md` behaves like a dashboard/map again
- tracked local result surfaces are explicitly local-only or registry-backed
- only approved bundle entry surfaces are indexed from `results/` and `Newton/phystwin_bridge/results/`
- `results/` keeps one family-root `README.md` per family while deeper local
  notes/verdicts stop using Markdown
- stale local mechanism guidance is explicitly labeled historical or
  non-reference-worthy instead of sounding like a recommended starting point
- generated inventory, staleness, and task-surface ledgers match the filesystem
- lint catches markdown truth drift, root clutter, and archive leakage mechanically
- hooks allow read-only inspection of watched surfaces while still guarding risky mutation/publish flows
- future agent summaries are steered toward changes/problems/findings/artifacts/next step, not process diaries

## Related Pages

- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
- [rope_perf_apples_to_apples.md](./rope_perf_apples_to_apples.md)
- [2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
- [../../newton/robot_example_patterns.md](../../newton/robot_example_patterns.md)
