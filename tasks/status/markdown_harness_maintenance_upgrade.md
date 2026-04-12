> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-11`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation. Keep the page outcome-first rather than process-first.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

This maintenance line is active and currently healthy:

- the robot + deformable line stays retired as historical context only
- active task/status surfaces are short enough to function as live control-plane pages
- the maintenance queue is quiet instead of permanently noisy
- harness lint currently passes

## What Changed In The Latest Pass

- moved long self-collision scratch notes into:
  - `tasks/history/status/self_collision_transfer_diagnostic_log_20260401_20260408.md`
- moved long bunny rollout chronology into:
  - `tasks/history/status/bunny_penetration_force_diagnostic_log_20260401.md`
- rewrote the active self-collision and bunny surfaces so they now report:
  - current state
  - last completed step
  - next step
  - current artifact paths
- cleaned the generated-doc story so the current maintenance path points only at
  the `md_*` reports
- wrapped the long review-PDF command in `tasks/implement/slide_deck_overhaul.md`
- narrowed `md_staleness_report` so historical archive length no longer keeps
  the queue permanently red

## Problem Solved

- active task/status pages no longer masquerade as scratch notebooks
- the current generated maintenance reports now reflect the real day-to-day path
- the maintenance queue is quiet enough to trust

## Findings / Conclusions

- the repo did not need another harness; it needed active surfaces to stop absorbing historical detail
- maintenance reports are only useful when historical bulk is pushed out of the live control plane
- once a generated ledger's role has been absorbed by the current `md_*` reports, it should be retired instead of kept as a parallel maintenance surface

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
- `docs/generated/md_staleness_report.md` is currently clean

## Validation

- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `python -m py_compile .codex/hooks/session_start.py .codex/hooks/post_tool_use_review.py .codex/hooks/stop_continue.py`
- current result after this pass: `PASS`
