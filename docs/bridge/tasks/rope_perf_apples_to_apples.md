> status: active
> canonical_replacement: none
> owner_surface: `rope_perf_apples_to_apples`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when benchmark rows, claim boundary, or promoted performance evidence changes.`
> notes: Active canonical task page for the same-case rope replay benchmark.

# Task: Rope Perf Apples To Apples

## Question

For the same `rope_double_hand` replay case, same controller trajectory, same
`dt`, same substeps, same GPU, and rendering disabled:

1. Is Newton faster or slower than PhysTwin?
2. If Newton is slower, where exactly is the time going?
3. Only after that, which optimization path is actually justified?

## Why It Matters

Professor feedback is explicit: the project must first establish a clean
apples-to-apples rope benchmark before discussing optimization. A generic
"interactive playground is slow" claim is not sufficient.

## Current Status

- Completed for the current meeting scope
- Canonical result root:
  - `results/rope_perf_apples_to_apples/`
- Key result:
  - Newton A1 precomputed replay is still about `3.30x` slower than PhysTwin
    B0 headless replay in `ms/substep`
- Key explanation:
  - controller bridge tax is real (`~1.87x` A0 -> A1)
  - collision is not the main cause on the pure rope replay baseline
  - Nsight supports a graph-launch / execution-structure explanation for the
    remaining gap

## Code Entry Points

- Main Newton script:
  - `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
- Main PhysTwin simulator path:
  - `PhysTwin/qqtt/engine/trainer_warp.py`
  - `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`
- Relevant bridge/report code:
  - `scripts/`
  - `formal_slide/meeting_2026_04_01/`

## Canonical Commands

- Newton A0/A1/A2/A3 should use `demo_rope_control_realtime_viewer.py` in
  `--profile-only` mode with `--viewer null`
- PhysTwin B0/B1 should use a headless harness that replays the same
  `rope_double_hand` controller trajectory without GUI or Gaussian rendering

## Required Artifacts

- apples-to-apples benchmark table
- per-stage `summary.json`
- per-stage `manifest.json`
- per-stage `command.txt`
- per-stage `stdout.log` / `stderr.log`
- written methodology and conclusion pages
- profiling slide asset update
- Nsight A1/B0 traces

## Success Criteria

- Same rope case comparison is established with rendering excluded
- Newton throughput and attribution both exist
- PhysTwin headless throughput exists
- The gap is quantified in `ms/substep` and `RTF`
- The gap explanation separates bridge tax from remaining simulator/runtime cost
- Only then an optimization roadmap is proposed

## Open Questions

- How much of the remaining gap can be closed by more graph-like or more batched
  Newton replay execution without changing physics settings?
- After execution-structure cleanup, which Newton kernels remain worth
  micro-optimizing first?

## Related Pages

- [interactive_playground_profiling.md](./interactive_playground_profiling.md)
- [../current_status.md](../current_status.md)
- [../open_questions.md](../open_questions.md)
