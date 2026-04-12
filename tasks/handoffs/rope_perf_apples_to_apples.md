# Handoff: rope_perf_apples_to_apples

## Current Milestone

Preserve the promoted apples-to-apples rope replay benchmark as the current
performance truth surface.

## What Changed

- the task now has an explicit contract/handoff pair because it is a
  result-bearing benchmark workflow

## Current Conclusion

`20260401_rope_perf_meeting_bundle` remains the committed benchmark authority.
`E1` visible-viewer context is still secondary and should not replace the
registry-backed no-render scope.

## Exact Next Command

```bash
python scripts/generate_md_inventory.py
```

## Current Blocker

No blocker for the current benchmark-closeout surface.

## Last Failed Acceptance Criterion

The task lacked an explicit contract/handoff despite owning a promoted
benchmark result.

## Key GIF / Artifact Paths

- `results_meta/tasks/rope_perf_apples_to_apples.json`
- `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md`
- `results/rope_perf_apples_to_apples/report/todo2_rope_perf_report.pdf`

## What Not To Redo

- do not promote viewer-only rows as the benchmark authority
- do not reopen optimization narrative drift inside the benchmark task without a new promoted benchmark change

## Missing Evidence

- none for the current promoted benchmark

## Context Reset Recommendation

- recommended: yes
- reason:
  - this task has a stable artifact tree and should resume from files, not chat
