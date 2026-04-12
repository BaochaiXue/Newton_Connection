# Handoff: markdown_harness_maintenance_upgrade

## Current Milestone

Repo-wide progressive-disclosure hardening after the initial fail-closed
cleanup pass.

## What Changed

- outcome-first reporting was added to AGENTS, task templates, and
  `docs/runbooks/agent_reporting.md`
- active entrypoints now route history through archive hubs instead of inline
  historical lists
- root-level reusable scripts/configs were moved under `scripts/`
- hook policy now aims for write-strict/read-loose behavior
- generator and lint now encode:
  - root allowlist auditing
  - approved bundle-entry quarantine
- `results/` now keeps one family-root `README.md` per family and demotes
  deeper local notes/verdicts to `.txt`
- robot-driving guidance now routes through
  `docs/newton/robot_example_patterns.md`, and archived bridge robot practices
  are treated as historical failure analysis rather than recommended templates
- smoke checks confirmed:
  - read-only access to watched files succeeds
  - direct execution of `scripts/send_pdf_via_yahoo.py` is still denied
- the same maintenance line still owns this work; no parallel cleanup task was
  created

## Current Conclusion

The repo still does not need another harness. The load-bearing fixes are:
progressive disclosure in live entrypoints, less root clutter, approved
bundle-entry quarantine, hooks that stop confusing path names with risky
actions, explicit routing away from stale local robot-practice guidance, and
family-root-only Markdown browsing under `results/`.

## Exact Next Command

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```

## Current Blocker

No structural blocker. Remaining work is routine upkeep: preserve the archive
hub rule, root allowlist, bundle-entry quarantine, and write-strict/read-loose
hook semantics.

## Last Failed Acceptance Criterion

Active entrypoints and hooks were still noisy enough that agents could wander
into history or get blocked during read-only inspection.

## Key GIF / Artifact Paths

- `docs/runbooks/agent_reporting.md`
- `docs/newton/robot_example_patterns.md`
- `docs/archive/tasks/README.md`
- `docs/bridge/tasks/README.md`
- `docs/bridge/current_status.md`
- `results/README.md`
- `results/rope_perf_apples_to_apples/README.md`
- `.codex/hooks/session_start.py`
- `.codex/hooks/pre_tool_use_policy.py`
- `.codex/hooks/post_tool_use_review.py`
- `.codex/hooks/stop_continue.py`
- `scripts/demote_results_markdown.py`
- `scripts/md_truth_inventory_lib.py`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`
- `docs/generated/md_staleness_report.md`
- `docs/generated/task_surface_matrix.md`

## What Not To Redo

- do not create a second reporting runbook
- do not reopen a parallel harness-maintenance task for the same issue
- do not re-expand active indexes into inline historical ledgers
- do not reintroduce reusable scripts at repo root
- do not let closeouts fall back to deleted/archived file inventories as the
  main story

## Missing Evidence

- fresh future turns showing the navigation and hook rules hold without manual
  correction

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task is about durable repo state, so a fresh agent should be able to
    resume from files instead of chat memory
