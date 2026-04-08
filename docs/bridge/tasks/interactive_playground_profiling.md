> status: active
> canonical_replacement: none
> owner_surface: `interactive_playground_profiling`
> last_reviewed: `2026-04-08`
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

For strict one-to-one controller-replay profiling against PhysTwin on the same
interactive-playground case, use the bridge-side wrapper around:

- `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
- `scripts/benchmark_phystwin_rope_headless.py`
- `scripts/profile_phystwin_playground_kernels.py`
- `scripts/run_interactive_playground_apples_to_apples.sh`

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

Latest exploratory same-case interactive-playground bundle:

- `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`

Meeting-facing summary surface for that latest rope cross-check:

- `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - slide `9`
  - title:
    `Result P2: Latest One-To-One Rope Matchup Preserves The Same Story`

This run uses:

- same case on both sides:
  - `rope_double_hand`
- render disabled on both sides
- Newton baseline and precomputed controller replay throughput
- Newton granular attribution
- PhysTwin graph-on throughput
- PhysTwin kernel-level attribution

Current exploratory conclusion from that run:

- Newton baseline is about `6.66x` slower than PhysTwin on this rope case
- even after precomputing controller writes, Newton is still about `3.54x`
  slower
- precomputing controller writes still matters on rope:
  - about `1.88x` speedup over Newton baseline
- on rope, collision candidate generation is absent on both sides and is not the
  bottleneck story
- the heavier Newton costs are the solver/integration/spring/controller-replay
  structure around the same rope controller path

Earlier same-case cloth exploratory run retained for comparison:

- `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`

## Required Artifacts

- JSON profile summary
- CSV profile summary
- short written interpretation

## Success Criteria

- mean ± std reported
- render and physics clearly separated
- meeting-ready conclusion without overclaiming
