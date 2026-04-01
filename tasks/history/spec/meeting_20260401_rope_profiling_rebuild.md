> status: historical
> canonical_replacement: none
> owner_surface: `meeting_20260401_rope_profiling_rebuild`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Keep only as a historical spec for the completed 2026-04-01 profiling-section rewrite.`
> notes: Historical one-off spec moved out of `tasks/spec/` so it no longer reads like active work.

# Spec: meeting_20260401_rope_profiling_rebuild

## Goal

Rebuild the 2026-04-01 rope profiling section into a plain-language,
real-viewer-relevant story supported by a clean rope benchmark matrix and
honest core/system evidence.

## Inputs

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- `results/rope_perf_apples_to_apples/`
- `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
- `Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py`
- `Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py`
- `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`

## Outputs

- updated deck source and transcript
- refreshed `results/rope_perf_apples_to_apples/summary.json`
- refreshed profiling audit markdown
- regenerated:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/transcript.pdf`

## Constraints

- `Newton/newton/` is read-only
- rope case only
- no plots/charts/self-drawn diagrams in the profiling section
- wrapper code may define benchmark methodology, but not core execution claims
- transcript must explain each page in normal spoken language

## Done When

- Q1-Q4 are answered in order
- E1-E4 are explicitly defined on the slides
- real-viewer relevance is stated directly
- shorthand terms like `bridge tax` and `launch-dominated` are removed from slides
- the deck builds successfully
