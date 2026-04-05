# Contract: markdown_harness_maintenance_upgrade / reporting-discipline-hardening

## Goal

Make future Codex summaries in this repo outcome-first by encoding the
reporting contract into repo-visible instructions and hooks.

## Scope Boundary

- In scope:
  - repo-visible reporting rules for user-facing summaries
  - startup/post-tool/stop-hook guidance for outcome-first reporting
  - maintenance task-chain updates that describe the new reporting contract
  - keeping the reporting rule aligned with the existing markdown harness
- Out of scope:
  - Newton core changes
  - experiment reruns
  - unrelated result-authority cleanups

## Required Inputs

- `AGENTS.md`
- `tasks/AGENTS.md`
- `docs/runbooks/agent_reporting.md`
- `docs/runbooks/doc_gardening.md`
- `.codex/hooks/session_start.py`
- `.codex/hooks/post_tool_use_review.py`
- `.codex/hooks/stop_continue.py`
- active markdown-maintenance task-chain files

## Required Outputs

- explicit reporting runbook
- AGENTS/tasks-AGENTS guidance for outcome-first summaries
- hook reminders/blockers that reduce process-first completion reports
- regenerated generated ledgers after the control-plane edits

## Hard-Fail Conditions

- the repo still lacks a clear reporting contract for user-facing summaries
- hooks still tolerate process-heavy completion messages without any steer
- reporting expectations still live only in chat, not in versioned files

## Acceptance Criteria

- `python scripts/generate_md_inventory.py` regenerates without ambiguity
- `python scripts/lint_harness_consistency.py` passes
- `AGENTS.md` tells future agents to report changes, solved problems, findings,
  conclusions, artifact paths, and next steps
- `docs/runbooks/agent_reporting.md` exists as the canonical reporting runbook
- the hooks now remind or lightly block against meta-heavy completion messages

## Evaluator Evidence Required

- validator command(s):
  - `python scripts/generate_md_inventory.py`
  - `python scripts/lint_harness_consistency.py`
- artifact paths:
  - `docs/runbooks/agent_reporting.md`
  - `docs/generated/md_inventory.md`
  - `docs/generated/md_cleanup_report.md`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```
