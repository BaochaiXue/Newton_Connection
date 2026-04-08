# Status: interactive_playground_profiling

## Current State

Tracked as an active exploratory task.

The committed current rope benchmark truth does not live here. For the
authoritative same-case replay benchmark, use:

- `results_meta/tasks/rope_perf_apples_to_apples.json`
- `tasks/status/rope_perf_apples_to_apples.md`

## Last Completed Step

Added the missing spec/plan/implement/status scaffold during the harness
upgrade.

Rebuilt the 2026-04-01 TODO 2 profiling slides so the meeting-facing rope
story now treats this task as methodology context only; the authoritative gap
evidence itself remains under `rope_perf_apples_to_apples`.

## 2026-04-08 Same-Case One-To-One Run

- Earlier cloth same-case exploratory bundle retained:
  - `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`
  - useful as a cloth interactive counterexample where collision candidate generation dominates

## 2026-04-08 Rope Interactive Playground One-To-One Run

- New exploratory bundle:
  - `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`
- Same-case scope:
  - `rope_double_hand`
  - same controller trajectory on both sides
  - render disabled on both sides
- Newton stages:
  - `N0_baseline_throughput`
  - `N1_precomputed_throughput`
  - `N2_baseline_attribution`
  - `N3_precomputed_attribution`
- PhysTwin stages:
  - `P0_headless_throughput`
  - `P1_kernel_attribution`
- Primary outputs:
  - `comparison/comparison.md`
  - `comparison/throughput_summary.csv`
  - `comparison/operation_matchup_raw.csv`
  - `comparison/operation_matchup_grouped.csv`

## Current Rope Conclusion

- Throughput:
  - Newton baseline:
    `0.067757 ms/substep`
  - Newton precomputed:
    `0.036062 ms/substep`
  - PhysTwin graph headless:
    `0.010175 ms/substep`
- Same-case slowdown:
  - Newton baseline vs PhysTwin:
    `6.659x`
  - Newton precomputed vs PhysTwin:
    `3.544x`
  - Newton precomputed speedup over Newton baseline:
    `1.879x`
- Bottleneck interpretation on rope:
  - controller target upload is real on Newton rope replay:
    - baseline upload:
      `0.040093 ms/substep`
    - precomputed upload:
      `n/a`
  - but after removing that tax, Newton still remains materially slower
  - current Newton top amortized substep costs on rope are:
    - `solver_step`
    - `integrate_particles`
    - `spring_forces`
    - `drag_correction`
    - controller upload or `write_kinematic_state`
  - collision candidate generation is not the rope bottleneck story on either side:
    - Newton:
      `n/a`
    - PhysTwin:
      `n/a`
  - the main one-to-one rope gap is instead around:
    - spring-force evaluation
      - Newton:
        `0.021012-0.022576 ms/substep`
      - PhysTwin:
        `0.029981 ms/substep`
    - integration and drag
      - Newton:
        `0.044670-0.046353 ms/substep`
      - PhysTwin:
        `0.032785 ms/substep`
    - plus Newton's heavier solver-step shell:
      - `solver_step ≈ 0.070-0.072 ms/substep`
  - therefore rope and cloth now tell two different stories:
    - cloth interactive case:
      collision-generation dominates the cross-system gap
    - rope interactive case:
      controller tax matters, but the remaining gap is better explained by the
      broader solver/runtime structure than by collision generation

## Next Step

Keep the scope split explicit:

- clean replay truth remains under `rope_perf_apples_to_apples`
- this task should only hold new exploratory profiling work until a new result
  is promoted into `results_meta/`
- next exploratory step should test whether the same collision-generation gap
  still dominates on a weaker-contact or viewer-on playground scene, instead of
  assuming the clean rope replay conclusion transfers automatically

## Blocking Issues

- Scope split between clean replay and weak-contact profiling still needs to be explicit

## Artifact Paths

- `results_meta/tasks/rope_perf_apples_to_apples.json`
- exploratory interactive bundle:
  - `results/interactive_playground_profiling/runs/20260408_090500_rope_interactive_one_to_one_v1`
  - older cloth exploratory counterexample:
    `results/interactive_playground_profiling/runs/20260408_075949_blue_cloth_interactive_one_to_one_v1`
- related slide/report assets
