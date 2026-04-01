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

A no-render profiling path already exists and has produced early evidence that:

- collision is the largest single hotspot
- decoupled stepping adds major structural overhead
- Newton core itself should not be simplistically labeled “slow”

## Required Artifacts

- JSON profile summary
- CSV profile summary
- short written interpretation

## Success Criteria

- mean ± std reported
- render and physics clearly separated
- meeting-ready conclusion without overclaiming
