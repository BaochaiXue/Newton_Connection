> status: active
> canonical_replacement: none
> owner_surface: `interactive_playground_profiling`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when exploratory profiling scope or the boundary against committed rope benchmark truth changes.`
> notes: Methodology/umbrella profiling page only. Committed same-case rope benchmark truth belongs to `rope_perf_apples_to_apples`.

# Task: Interactive Playground Profiling

## Question

What is the true performance bottleneck of the Newton interactive playground?

## Why It Matters

The advisor explicitly asked for profiling without guessing.

## Main Script

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`

## Method

- disable rendering first
- run repeated profiling episodes
- separate:
  - collision generation
  - solver path
  - decoupled multi-kernel overhead
  - render cost

## Current Status

This task is exploratory methodology, not the committed result-authority surface
for the rope replay benchmark.

Use it to hold:

- new profiling hypotheses
- non-promoted exploratory bundles
- profiling method questions such as clean replay vs weak-contact scenes

For the committed same-case rope replay benchmark and its current conclusion,
use:

- `docs/bridge/tasks/rope_perf_apples_to_apples.md`
- `tasks/status/rope_perf_apples_to_apples.md`
- `results_meta/tasks/rope_perf_apples_to_apples.json`

## Required Artifacts

- JSON profile summary
- CSV profile summary
- short written interpretation

## Success Criteria

- mean ± std reported
- render and physics clearly separated
- meeting-ready conclusion without overclaiming
