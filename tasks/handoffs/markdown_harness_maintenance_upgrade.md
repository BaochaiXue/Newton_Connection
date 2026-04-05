# Handoff: markdown_harness_maintenance_upgrade

## Current Milestone

Semantic-hardening follow-up after the initial fail-closed cleanup pass.

## What Changed

- outcome-first reporting was added to AGENTS, task templates, and
  `docs/runbooks/agent_reporting.md`
- stop hooks now push back on bookkeeping-first closeouts
- the same maintenance line still owns this work; no parallel cleanup task was
  created

## Current Conclusion

The missing harness piece was reporting discipline, not another task system.
Future summaries should now default to changes, solved problems, conclusions,
artifacts, and next steps.

## Exact Next Command

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```

## Current Blocker

No structural blocker. Remaining work is routine metadata upkeep, not another
reporting-design pass.

## Last Failed Acceptance Criterion

Agent closeouts were still too bookkeeping-heavy even after validation and
authority drift were hardened.

## Key GIF / Artifact Paths

- `docs/runbooks/agent_reporting.md`
- `.codex/hooks/session_start.py`
- `.codex/hooks/post_tool_use_review.py`
- `.codex/hooks/stop_continue.py`
- `docs/generated/md_staleness_report.md`
- `docs/generated/task_surface_matrix.md`

## What Not To Redo

- do not create a second reporting runbook
- do not reopen a parallel harness-maintenance task for the same issue
- do not let closeouts fall back to deleted/archived file inventories as the
  main story

## Missing Evidence

- fresh future turns showing the new closeout discipline holds without manual
  correction

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task is about durable repo state, so a fresh agent should be able to
    resume from files instead of chat memory
