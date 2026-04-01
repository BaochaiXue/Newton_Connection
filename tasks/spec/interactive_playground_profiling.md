# Spec: interactive_playground_profiling

## Goal

Explain the Newton interactive playground bottleneck with no-render, data-backed
profiling rather than guesses.

## Non-Goals

- Declaring Newton core “slow” without attribution
- Mixing weak-contact cases and clean replay cases into one conclusion

## Inputs

- `docs/bridge/tasks/interactive_playground_profiling.md`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
- profiling outputs and follow-up notes

## Outputs

- JSON/CSV summaries
- short written interpretation
- separation of render, collision, solver-path, and structural overhead

## Constraints

- disable rendering first
- keep the interpretation evidence-based

## Done When

- the true hotspot split is written down
- render and physics are separated cleanly
- follow-up optimization work has a bounded next step
