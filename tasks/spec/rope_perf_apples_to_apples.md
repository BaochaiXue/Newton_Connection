# Spec: rope_perf_apples_to_apples

## Goal

Produce a defensible apples-to-apples rope performance investigation that
compares Newton rope replay against PhysTwin headless replay under the same
case, same controller trajectory, same `dt`, same substeps, same GPU, and no
rendering.

## Non-Goals

- Optimizing Newton before the comparison and bottleneck explanation are done
- Using contact-heavy robot scenes as the primary performance conclusion
- Using rendering-inclusive timing as the main benchmark

## Inputs

- Newton rope strict IR:
  - `Newton/phystwin_bridge/ir/rope_double_hand/phystwin_ir_v2_bf_strict.npz`
- Newton rope replay benchmark:
  - `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
- PhysTwin rope case data:
  - `PhysTwin/data/different_types/rope_double_hand/final_data.pkl`
- PhysTwin trained checkpoint + optimal params:
  - `PhysTwin/experiments/rope_double_hand/train/best_*.pth`
  - `PhysTwin/experiments_optimization/rope_double_hand/optimal_params.pkl`

## Outputs

- `results/rope_perf_apples_to_apples/README.md`
- `results/rope_perf_apples_to_apples/BEST_EVIDENCE.md`
- `results/rope_perf_apples_to_apples/index.csv`
- `results/rope_perf_apples_to_apples/newton/A0_baseline_throughput/`
- `results/rope_perf_apples_to_apples/newton/A1_precomputed_throughput/`
- `results/rope_perf_apples_to_apples/newton/A2_baseline_attribution/`
- `results/rope_perf_apples_to_apples/newton/A3_precomputed_attribution/`
- `results/rope_perf_apples_to_apples/phystwin/B0_headless_throughput/`
- `results/rope_perf_apples_to_apples/phystwin/B1_headless_attribution/`
- `results/rope_perf_apples_to_apples/notes/methodology.md`
- `results/rope_perf_apples_to_apples/notes/conclusions.md`
- `results/rope_perf_apples_to_apples/notes/open_questions.md`

## Constraints

- `Newton/newton/` is read-only
- Use the same `rope_double_hand` case and same controller trajectory on both
  sides
- Keep rendering excluded from the primary comparison
- Do not change `dt` or substeps just to improve numbers
- Be explicit if PhysTwin attribution is shallower than Newton attribution

## Done When

- A0/A1/A2/A3 exist and are organized
- B0 exists and is organized
- B1 exists if practical, otherwise limitations are documented clearly
- Benchmark table quantifies Newton vs PhysTwin and baseline vs precomputed
- Bottleneck explanation is evidence-based
- Optimization roadmap is proposed only after the explanation
- Profiling slide/material assets are updated
