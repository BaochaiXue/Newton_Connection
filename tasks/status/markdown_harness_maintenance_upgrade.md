> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

Completed for the current semantic-hardening follow-up after the initial
2026-04-01 cleanup pass.

This pass was structural cleanup plus workflow hardening, not routine
housekeeping only.

## Audited Issues

- `remote_interaction_root_cause` had a full active chain in execution
  directories but was missing from the canonical active task index
- `robot_rope_franka` local manifests still drifted from the registry-backed
  current run and local-only policy:
  - root `manifest.json` still pointed at the old `c08` run
  - `BEST_RUN/manifest.json` still used promoted-best wording and
    machine-local absolute paths
- `rope_perf_apples_to_apples` wording had started to broaden the
  registry-backed no-render claim boundary by treating visible-viewer `E1` as
  part of the committed meaning rather than supporting context
- generated maintenance reports were still too noisy:
  - `md_staleness_report.md` behaved like a permanent red backlog
  - `md_cleanup_report.md` still dumped too many low-signal `REFORMAT` rows
- contracts and handoffs still existed mostly as templates and were not yet
  demonstrably used by a live active task

## Changes Implemented

- continued the same maintenance line rather than opening a second overlapping
  cleanup task
- indexed `remote_interaction_root_cause` in `docs/bridge/tasks/README.md` and
  surfaced it in `docs/bridge/current_status.md`, removing the hidden-active
  chain problem
- corrected `robot_rope_franka` local manifest authority drift:
  - root `manifest.json` now mirrors the current `c10` local run id
  - `BEST_RUN/manifest.json` now uses local-only mirror wording, relative paths,
    and an explicit `authoritative_source`
- narrowed `rope_perf_apples_to_apples` wording so the registry-backed current
  meaning remains the no-render apples-to-apples benchmark and `E1` stays
  supporting context only
- made the blocked self-collision `FINAL_STATUS.md` more explicit as an older
  local blocked snapshot, not the latest parity numbers
- narrowed maintenance-report actionability:
  - `md_staleness_report.md` now covers the enforced high-signal review scope
    plus genuinely overgrown/compressed surfaces
  - `md_cleanup_report.md` now emphasizes actionable archive/stub/reformat
    decisions instead of every possible low-signal row
- extended `task_surface_matrix.md` to show real contract/handoff usage rather
  than only chain existence and registry backing
- converted contracts/handoffs from pure template status to selective live use
  by adding:
  - `tasks/contracts/markdown_harness_maintenance_upgrade.md`
  - `tasks/handoffs/markdown_harness_maintenance_upgrade.md`
- updated `tasks/contracts/README.md` and `tasks/handoffs/README.md` so they
  honestly describe current status as selectively load-bearing rather than
  universally mature

## Remaining Blockers

- no blocker for the completed semantic-hardening pass
- remaining maintenance debt is review-age metadata rollout across older
  high-value
  supporting surfaces that still appear in the narrowed staleness queue

## Exact Next Step

- use the narrowed staleness queue for the next routine metadata pass rather
  than opening another overlapping cleanup task
- keep future hidden subtask chains out of active execution directories unless
  they are also indexed in the live task map
- continue review-age cleanup only on the narrowed high-signal scope reported by
  `docs/generated/md_staleness_report.md`

## Validation Commands Run

- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- final result after the latest semantic-hardening changes: `PASS`
- targeted audit reads over:
  - `docs/bridge/current_status.md`
  - `docs/bridge/tasks/README.md`
  - `tasks/status/rope_perf_apples_to_apples.md`
  - `tasks/status/self_collision_transfer.md`
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka/manifest.json`
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/manifest.json`

## Current Pass Type

- structural cleanup: yes
- routine maintenance: yes
- contract used: yes
- handoff used: yes
