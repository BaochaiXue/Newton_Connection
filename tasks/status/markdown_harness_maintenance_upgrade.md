> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-05`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation. Keep the page outcome-first rather than process-first.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

Active again for a narrow follow-up: future Codex reports still overemphasize
maintenance choreography instead of changes, solved problems, conclusions,
artifacts, and next steps.

## What Changed This Pass

- added a canonical reporting runbook at `docs/runbooks/agent_reporting.md`
- tightened `AGENTS.md`, `tasks/AGENTS.md`, and status/handoff templates around
  outcome-first reporting
- reinforced the reporting contract in:
  - `.codex/hooks/session_start.py`
  - `.codex/hooks/post_tool_use_review.py`
  - `.codex/hooks/stop_continue.py`
- expanded the active maintenance task/spec/plan/implement pages so reporting
  discipline is part of the harness scope
- cleared the remaining lint blockers exposed during this follow-up:
  - re-synced the active task index with active robot follow-on chains
  - removed stale active metadata from the archived
    `robot_sphere_inflation_root_cause` task page
  - removed the last machine-local markdown links from:
    - `tasks/status/native_robot_physical_blocking_minimal.md`
    - `tasks/status/robot_rope_franka_physical_blocking.md`
    - `tasks/status/robot_visible_rigid_tool_baseline.md`
- preserved the earlier semantic-hardening wins:
  - hidden active chains are indexed
  - local manifest authority drift is fixed
  - maintenance reports are narrower and more actionable

## Problem Solved

- future agents now get a durable repo-native instruction to report:
  - what changed
  - what problem was solved
  - what conclusion now holds
  - what artifact is worth checking
  - what the next step is
- closeouts are now less likely to lead with `Before vs After`, deleted/archived
  file lists, or validation-command inventories

## Findings / Conclusions

- the earlier harness already enforced validation and authority reasonably well
- the missing piece was reporting discipline, not another parallel harness
- the right fix was to encode the reporting contract in four places:
  - entrypoint rules
  - runbooks
  - templates
  - stop-hook enforcement
- the final lint pass also confirmed that the residual archive/path leaks
  exposed during validation are now closed

## GIF / Artifact Paths To Review

- no new GIF belongs to this maintenance pass
- main evidence to inspect:
  - `docs/runbooks/agent_reporting.md`
  - `AGENTS.md`
  - `.codex/hooks/session_start.py`
  - `.codex/hooks/post_tool_use_review.py`
  - `.codex/hooks/stop_continue.py`

## Next Step

- keep using the new outcome-first summary contract in future turns
- watch whether any future final report still trips the new stop-hook heuristic
- continue review-age cleanup only on the narrowed high-signal scope reported by
  `docs/generated/md_staleness_report.md`

## Blocking Issues

- no blocker for the reporting-discipline hardening itself
- remaining maintenance debt is still the narrowed review-age metadata queue on
  older high-value supporting surfaces

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `python -m py_compile .codex/hooks/session_start.py .codex/hooks/post_tool_use_review.py .codex/hooks/stop_continue.py`
- current expected result after this pass: `PASS`
