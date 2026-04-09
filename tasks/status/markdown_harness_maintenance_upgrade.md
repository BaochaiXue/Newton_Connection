> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-09`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation. Keep the page outcome-first rather than process-first.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

Current follow-up completed for this pass: the robot + deformable PS-object
line is now retired as a historical decision, its active control-plane surfaces
are gone, the bridge-side robot demo entrypoints are deleted, and the latest
harness lint passes on the cleaned repo state.

## What Changed This Pass

- added a canonical reporting runbook at `docs/runbooks/agent_reporting.md`
- tightened `AGENTS.md`, `tasks/AGENTS.md`, and status/handoff templates around
  outcome-first reporting
- retired the full bridge-side robot + deformable PS-object line as a failed
  final claim and added one canonical retrospective:
  - `docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
- moved the remaining robot task chains out of live task neighborhoods:
  - `robot_deformable_demo`
  - `robot_rope_franka_tabletop_push_hero`
  - `robot_rope_true_size_recalibration`
  - `robot_rope_franka_semiimplicit_oneway`
  - `robot_rope_franka_physical_blocking`
  - `native_robot_physical_blocking_minimal`
  - `robot_visible_rigid_tool_baseline`
  - `native_robot_rope_drop_release`
- removed robot demo surfaces from:
  - `docs/bridge/tasks/README.md`
  - `docs/bridge/current_status.md`
  - `TODO.md`
  - `docs/PROJECT_MAP.md`
  - `docs/bridge/demos_and_diagnostics.md`
- downgraded robot result-authority surfaces from promoted live truth to
  historical evidence in `results_meta/`
- deleted bridge-side robot demo entrypoints and their dedicated wrappers /
  validators so the repo no longer pretends that the robotics line is still a
  runnable current demo family
- archived the stale / non-active robot predecessor chains out of live task
  neighborhoods:
  - `remote_interaction_root_cause`
  - `robot_rope_franka_native_v2`
  - `robot_rope_franka_split_v3`
- moved their task pages into `docs/archive/tasks/`, their plans into
  `plans/completed/`, and their execution-layer surfaces into `tasks/history/`
- marked those moved files as historical so they stop sounding current
- removed `remote_interaction_root_cause` from the active task index and moved
  the three archived robot surfaces into the historical section
- rewrote `docs/bridge/current_status.md` back toward a real dashboard instead
  of a mixed dashboard + task ledger
- reinforced the reporting contract in:
  - `.codex/hooks/session_start.py`
  - `.codex/hooks/post_tool_use_review.py`
  - `.codex/hooks/stop_continue.py`
- expanded the active maintenance task/spec/plan/implement pages so reporting
  discipline is part of the harness scope
- cleared the remaining lint blockers exposed during this follow-up:
- preserved the earlier semantic-hardening wins:
  - hidden active chains are no longer left in active neighborhoods
  - local manifest authority drift is fixed
  - maintenance reports are narrower and more actionable

## Problem Solved

- active directories no longer contain three stale robot/predecessor chains
  that competed with the actual active task map
- the bridge task index and dashboard now point at the live surfaces again
- outcome-first reporting rules no longer exist in duplicated near-copy form
- the repo no longer presents failed robot + deformable partial baselines as
  current active work or promoted committed truth
- dead bridge-side robot demos and dedicated wrappers are gone from the active
  code surface, so future agents are less likely to restart the failed line by
  accident

## Findings / Conclusions

- the repo did not need another harness; it needed stale robot branches and
  completed investigations moved out of live-looking neighborhoods
- `docs/bridge/current_status.md` had drifted back toward a duplicate task
  ledger; trimming it is part of truth maintenance, not cosmetic editing
- the duplicated reporting rules in `AGENTS.md` and `tasks/AGENTS.md` were
  low-grade harness residue and are now collapsed into single canonical rules
- the robot + deformable line produced useful mechanism studies and historical
  partial baselines, but it never reached a meeting-grade combined success and
  should not remain promoted or runnable by default

## GIF / Artifact Paths To Review

- no new GIF belongs to this maintenance pass
- main evidence to inspect:
  - `docs/bridge/current_status.md`
  - `docs/bridge/tasks/README.md`
  - `docs/archive/tasks/robot_rope_franka_native_v2.md`
  - `docs/archive/tasks/robot_rope_franka_split_v3.md`
  - `docs/archive/tasks/remote_interaction_root_cause.md`

## Next Step

- keep trimming or archiving any future robot/predecessor branch that stops
  driving the active task map
- keep review-age cleanup focused on the narrowed high-signal queue instead of
  reopening broad structural cleanup
- if the project reopens robot + deformable work later, it must start from a
  new decision-bound task chain instead of reviving the retired demo surfaces

## Blocking Issues

- no blocker for this cleanup pass
- remaining maintenance debt is the smaller review-age / reformat queue still
  listed in `docs/generated/md_staleness_report.md`

## Validation

- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `python -m py_compile .codex/hooks/session_start.py .codex/hooks/post_tool_use_review.py .codex/hooks/stop_continue.py`
- current result after this pass: `PASS`
