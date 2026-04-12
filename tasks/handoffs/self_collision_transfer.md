# Handoff: self_collision_transfer

## Current Milestone

Preserve the reproducible blocked self-collision comparison as the current
authority while future fixes remain local mechanism work.

## What Changed

- the task now has an explicit contract/handoff pair because it is a blocked,
  result-bearing workflow
- the active status page was shortened and the older scratch chronology moved to
  `tasks/history/status/self_collision_transfer_diagnostic_log_20260401_20260408.md`

## Current Conclusion

The old large `case_3 > case_4` gap is no longer the main blocker. The current
blocked state is the broader controller-spring / rollout parity mismatch.

## Exact Next Command

```bash
python scripts/generate_md_inventory.py
```

## Current Blocker

The fair `2 x 2` matrix still misses the strict parity gate, and the remaining
gap sits outside simple ground-law isolation.

## Last Failed Acceptance Criterion

The task lacked an explicit contract/handoff even though it owns the current
blocked comparison surface.

## Key GIF / Artifact Paths

- `results_meta/tasks/self_collision_transfer.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607/final_verdict.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_visual_bundle_20260408_042645_00feebe/`

## What Not To Redo

- do not replace the committed blocked root with scratch diagnostics
- do not reopen broad self-collision experimentation without comparing against the current blocked roots

## Missing Evidence

- a future bridge-side fix that actually changes the blocked state

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task is blocked, multi-session, and has a nontrivial artifact tree
