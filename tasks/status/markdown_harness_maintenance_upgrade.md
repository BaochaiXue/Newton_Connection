> status: active
> canonical_replacement: none
> owner_surface: `markdown_harness_maintenance_upgrade`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update after each meaningful cleanup milestone and after final validation.`
> notes: Live status log for the current markdown/control-plane maintenance pass.

# Status: markdown_harness_maintenance_upgrade

## Current State

Completed for the resumed 2026-04-01 maintenance pass.

The repo already has the right harness shape. This pass finished the remaining
semantic cleanup needed so archived task pages, local result surfaces, and
generated ledgers tell one truthful current-vs-historical story.

## Audited Issues

- active-vs-historical leakage survived in the execution/task neighborhood:
  - `meeting_20260401_rope_profiling_rebuild` had completed but still lived in
    active execution directories before this pass
- several local result surfaces under `Newton/phystwin_bridge/results/` still
  read like plausible current authority:
  - superseded `final_self_collision_campaign_20260330_205935_4fdef39/README.md`
  - blocked-bundle `final_self_collision_campaign_20260331_033636_533f3d0/README.md`
  - blocked-bundle `final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md`
  - `robot_rope_franka/BEST_RUN/README.md`
- `tasks/status/slide_deck_overhaul.md` had accumulated contradictory current
  slide counts inside one live status block
- generated inventory/lint still need a final refresh after the archive and
  local-authority wording changes land

## Changes Implemented

- confirmed the active maintenance task chain remains the only canonical
  markdown-harness upgrade workstream
- carried the one-off `meeting_20260401_rope_profiling_rebuild` chain through
  the singular archive/history locations already established in the repo:
  - `docs/archive/tasks/meeting_20260401_rope_profiling_rebuild.md`
  - `plans/completed/meeting_20260401_rope_profiling_rebuild.md`
  - `tasks/history/spec/meeting_20260401_rope_profiling_rebuild.md`
  - `tasks/history/implement/meeting_20260401_rope_profiling_rebuild.md`
  - `tasks/history/status/meeting_20260401_rope_profiling_rebuild.md`
- introduced `docs/archive/tasks/README.md` and updated the live task index to
  route historical task pages there instead of leaving them beside active task
  pages
- tightened inventory/lint logic so the archive task neighborhood is visible to
  the harness and non-active task pages still living in `docs/bridge/tasks/`
  can be flagged mechanically
- downgraded the remaining risky self-collision campaign bundle surfaces into
  explicit local-only records and aligned `results_meta/tasks/self_collision_transfer.json`
  to say so
- verified `tasks/status/slide_deck_overhaul.md` now presents one coherent
  current deck/review workflow instead of contradictory current counts

## Remaining Blockers

- no remaining structural blocker for active-vs-historical separation
- remaining maintenance debt is the broader metadata/review-age rollout across
  older supporting surfaces surfaced by `docs/generated/md_staleness_report.md`

## Exact Next Step

- use `docs/generated/md_staleness_report.md` for the next batch of targeted
  metadata/review-age cleanup, starting with high-value canonical surfaces such
  as `AGENTS.md`, `docs/README.md`, `docs/bridge/open_questions.md`, and
  `results_meta/schema.md`
- keep future historical task pages out of `docs/bridge/tasks/` and place them
  directly into `docs/archive/tasks/`

## Validation Commands Run

- `python scripts/lint_harness_consistency.py`
  - current result during this resumed pass: `FAIL`
- `rg --files docs/bridge/tasks plans/active tasks/spec tasks/implement tasks/status | rg 'meeting_20260401_rope_profiling_rebuild|markdown_harness_maintenance_upgrade|markdown_truthfulness_cleanup|harness_engineering_upgrade'`
- `git status --short`
- `sed -n '1,260p' Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md`
- `python scripts/sync_results_registry.py`
- `python scripts/generate_md_inventory.py`
- `python scripts/lint_harness_consistency.py`
  - final result after regeneration: `PASS`
