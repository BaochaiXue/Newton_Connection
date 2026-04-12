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
- required-workflow tasks now have explicit contract/handoff coverage
- active entrypoints now route history through archive hubs instead of inline historical ledgers
- root-level tracked entry surfaces are cleaner and reusable scripts/config examples now live under `scripts/`
- read-only inspection of watched harness paths now succeeds while risky release/generation flows remain guarded
- harness lint currently passes

## What Changed In The Latest Pass

- refreshed the canonical markdown-harness task chain so it now explicitly
  covers:
  - progressive disclosure
  - root hygiene
  - approved deep-bundle entry surfaces
  - write-strict/read-loose hook semantics
- rewrote the live entrypoints so they behave more like maps:
  - `AGENTS.md`
  - `TODO.md`
  - `docs/bridge/tasks/README.md`
  - `docs/bridge/current_status.md`
  - `tasks/README.md`
- compressed archive visibility in the active task index:
  - active entrypoints now link to `docs/archive/tasks/README.md` and the
    retirement decision instead of enumerating archived task pages inline
- moved reusable root-level utilities under `scripts/`:
  - `scripts/render_answer_pdf.py`
  - `scripts/run_phystwin_newton_pipeline.sh`
  - `scripts/send_pdf_via_yahoo.local.example.json`
  - local-only:
    - `scripts/send_pdf_via_yahoo.py`
    - `scripts/send_pdf_via_yahoo.local.json`
- removed `imgui.ini` from tracked repo state and kept it as ignored local
  runtime state
- tightened hook behavior:
  - read-only inspection of watched harness paths now passes
  - direct execution of `scripts/send_pdf_via_yahoo.py` remains blocked
  - generation / validation flows still emit follow-up bookkeeping guidance
- extended the inventory/lint story:
  - `md_inventory.md` now exposes a `Bundle Entry` column
  - `md_cleanup_report.md` now audits root allowlist compliance
  - `md_cleanup_report.md` now records the approved bundle-entry policy
  - `scripts/lint_harness_consistency.py` now fails on:
    - inline archive leakage from active indexes
    - dated changelog sections in `current_status.md`
    - tracked root components outside the allowlist
    - unapproved deep-bundle Markdown entering the harness

## Problem Solved

- active entrypoints no longer compete with long historical file lists
- root-level reusable tools no longer masquerade as repo entry surfaces
- hooks no longer confuse read-only inspection with risky side effects
- generated ledgers now explain both root allowlist policy and deep-bundle
  quarantine instead of only classifying Markdown in isolation

## Findings / Conclusions

- the repo still did not need another harness; it needed stronger progressive
  disclosure inside the existing one
- archive hubs work better than inline historical lists for agent navigation
- root clutter is a harness problem, not only an aesthetics problem
- deep bundle trees can stay in place as long as only a small approved entry set
  is indexed into the control plane
- hook policy has to reason about actions, not only path names

## GIF / Artifact Paths To Review

- no new GIF belongs to this maintenance pass
- main evidence to inspect:
  - `docs/bridge/current_status.md`
  - `docs/bridge/tasks/README.md`
  - `docs/generated/md_inventory.md`
  - `docs/generated/md_cleanup_report.md`
  - `.codex/hooks/pre_tool_use_policy.py`
  - `.codex/hooks/post_tool_use_review.py`

## Next Step

- keep future historical routing compressed to archive hubs instead of
  re-expanding live indexes
- keep new root-level utilities out of repo root unless they are true entry
  surfaces
- if a new local bundle Markdown file needs harness visibility, add it
  explicitly as an approved entry surface instead of letting deep README sprawl
  leak back in

## Blocking Issues

- no blocker for this cleanup pass
- `docs/generated/md_staleness_report.md` is currently clean

## Validation

- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
- `head -n 6 docs/bridge/current_status.md`
- `head -n 6 scripts/send_pdf_via_yahoo.py`
- `scripts/send_pdf_via_yahoo.py --help`
- `python -m py_compile .codex/hooks/session_start.py .codex/hooks/post_tool_use_review.py .codex/hooks/stop_continue.py`
- `python -m py_compile .codex/hooks/pre_tool_use_policy.py`
- `python -m py_compile scripts/md_truth_inventory_lib.py scripts/generate_md_inventory.py scripts/lint_harness_consistency.py`
- current result after this pass: `PASS`
