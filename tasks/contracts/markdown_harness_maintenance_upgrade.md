# Contract: markdown_harness_maintenance_upgrade / progressive-disclosure-hardening

## Goal

Make the existing repo harness easier for agents to navigate by tightening
progressive disclosure, root hygiene, deep-bundle quarantine, and hook
semantics without creating a parallel control plane.

## Scope Boundary

- In scope:
  - repo-visible routing rules for active vs historical work
  - root-level tracked-file cleanup and explicit allowlist policy
  - startup/pre-tool/post-tool/stop-hook behavior for write-strict/read-loose operation
  - approved deep-bundle entry surfaces under `results/` and `Newton/phystwin_bridge/results/`
  - maintenance task-chain updates that describe the current harness contract
  - keeping the reporting rule aligned with the existing markdown harness
- Out of scope:
  - Newton core changes
  - mass relocation of historical bundle trees
  - unrelated experiment reruns

## Required Inputs

- `AGENTS.md`
- `TODO.md`
- `docs/bridge/tasks/README.md`
- `docs/bridge/current_status.md`
- `tasks/README.md`
- `tasks/AGENTS.md`
- `docs/runbooks/agent_reporting.md`
- `docs/runbooks/doc_gardening.md`
- `.codex/hooks/pre_tool_use_policy.py`
- `.codex/hooks/session_start.py`
- `.codex/hooks/post_tool_use_review.py`
- `.codex/hooks/stop_continue.py`
- `scripts/md_truth_inventory_lib.py`
- `scripts/generate_md_inventory.py`
- `scripts/lint_harness_consistency.py`
- active markdown-maintenance task-chain files

## Required Outputs

- active entrypoints that route current work first and history through archive hubs
- root-level reusable tools/config moved under `scripts/` and local runtime state removed from tracked root
- hook reminders/blockers that stay strict for mutation/publish flows without blocking read-only inspection
- lint/inventory rules that enforce the root allowlist and approved bundle-entry policy
- AGENTS/tasks-AGENTS guidance for outcome-first summaries
- regenerated generated ledgers after the control-plane edits

## Hard-Fail Conditions

- active indexes still enumerate archived task pages inline
- tracked root files outside the allowlist still compete with entry surfaces
- hooks still block read-only inspection just because a watched path appears in the command
- approved deep-bundle entry policy still lives only in chat, not in versioned files

## Acceptance Criteria

- `python scripts/generate_md_inventory.py` regenerates without ambiguity
- `python scripts/lint_harness_consistency.py` passes
- `AGENTS.md` encodes the canonical navigation contract and root-hygiene rule
- `docs/bridge/tasks/README.md` routes history through `docs/archive/tasks/README.md` instead of inline archive lists
- `docs/bridge/current_status.md` stays dashboard-like and avoids dated changelog sections
- root-level tracked files outside the allowlist are moved or removed from tracking
- hooks allow read-only inspection of watched paths and still guard mutation/publish flows
- `docs/runbooks/agent_reporting.md` remains the canonical reporting runbook

## Evaluator Evidence Required

- validator command(s):
  - `python scripts/generate_md_inventory.py`
  - `python scripts/lint_harness_consistency.py`
- behavior checks:
  - read-only command against a watched harness path succeeds
  - read-only command mentioning the PDF-send helper succeeds
  - risky mutation/publish command remains guarded
- artifact paths:
  - `docs/bridge/tasks/README.md`
  - `docs/bridge/current_status.md`
  - `docs/runbooks/agent_reporting.md`
  - `docs/generated/md_inventory.md`
  - `docs/generated/md_cleanup_report.md`
- skeptical review required: no

## Next Command After Acceptance

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```
