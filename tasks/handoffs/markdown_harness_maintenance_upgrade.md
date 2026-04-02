# Handoff: markdown_harness_maintenance_upgrade

## Current Milestone

Semantic-hardening follow-up after the initial fail-closed cleanup pass.

## Exact Next Command

```bash
python scripts/generate_md_inventory.py && python scripts/lint_harness_consistency.py
```

## Current Blocker

No structural blocker. Remaining work is about reducing report noise,
aligning local manifests with `results_meta`, and keeping workflow-usage status
honest.

## Last Failed Acceptance Criterion

`md_staleness_report.md` was too noisy to function as a maintenance queue, and
`robot_rope_franka` local manifests still drifted from the registry-backed
current run.

## Key Artifact Paths

- `docs/generated/md_cleanup_report.md`
- `docs/generated/md_staleness_report.md`
- `docs/generated/task_surface_matrix.md`
- `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
- `Newton/phystwin_bridge/results/robot_rope_franka/manifest.json`
- `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/manifest.json`

## What Not To Redo

- do not recreate a second inventory story
- do not expand `current_status.md` back into a ledger
- do not treat contracts/handoffs as universal boilerplate; keep them selective and honest

## Missing Evidence

- fresh regenerated reports after the narrowed staleness scope lands
- passing lint after the latest authority/index updates

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task is specifically about durable repo state, so the handoff should
    let a fresh agent continue without relying on chat archaeology
