# Performance Section Audit — 2026-04-01

## Scope

Audited the performance / profiling section of the 2026-04-01 meeting deck:

- full-deck slides `8-12`
- source files:
  - `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/todo_list.md`
  - `formal_slide/meeting_2026_04_01/README.md`
- media folders:
  - `formal_slide/meeting_2026_04_01/slides_assets/gif/`
  - `formal_slide/meeting_2026_04_01/gif/`
  - `formal_slide/meeting_2026_04_01/images/`
- generated outputs:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `tmp_vis/performance_analysis_20260401/bridge_meeting_20260401_performance_only_slides_8_12.pptx`
  - `tmp_vis/performance_analysis_20260401/bridge_meeting_20260401_performance_only_slides_8_12.pdf`

## Pre-Revision Audit

| Full-deck slide | Title before revision | Verdict | Main problem |
| --- | --- | --- | --- |
| 8 | `Method: Fair Rope Benchmark Before Optimization` | FAIL | No GIF/video anchor; too much prose on one slide |
| 9 | `Source Proof: Same Replay, Different Execution Style` | FAIL | Real code existed, but screenshots were too small and excerpts were too long |
| 10 | `Result: Newton A1 Is 3.30x Slower Than PhysTwin B0` | PARTIAL | Table logic was correct, but the section still lacked media support |
| 11 | `Result: Bridge Tax Is Real, But Not The Whole Gap` | FAIL | Dense text slide; attribution evidence was not visually scannable |
| 12 | `Nsight: Residual Gap Looks Like Launch Structure` | FAIL | Dense text slide; Nsight evidence was not visually scannable |

## Revisions Applied

- Preserved the scientific order:
  1. fair benchmark setup
  2. source proof
  3. benchmark result
  4. bridge-tax attribution
  5. Nsight explanation
- Added a dedicated performance GIF asset:
  - source: `slides_assets/gif/rope_drag_on_cmp2x3.gif`
  - embedded deck asset: `gif/rope_perf_case_anchor.gif`
- Replaced the small code screenshots with regenerated source-code excerpt assets:
  - `images/code_replay_semantics.png`
  - `images/code_granular_profile.png`
- Replaced two text-heavy result slides with generated chart assets:
  - `images/perf_attribution_breakdown.png`
  - `images/perf_nsight_breakdown.png`
- Moved detailed methodology, attribution detail, and Nsight reasoning out of slides and into `transcript.md`.
- Added `--slide-range` and `--out-pptx` to the builder so the performance-only slice can be rebuilt from the same source of truth.
- Documented the canonical full-deck and performance-only build commands in `README.md`.

## Post-Revision Slide Check

| Full-deck slide | Current title | Verdict | Evidence |
| --- | --- | --- | --- |
| 8 | `Hypothesis P1: Fair Benchmark Before Optimization` | PASS | Hypothesis-driven title; real rope GIF embedded; slide text reduced to four short benchmark rules |
| 9 | `Source Proof P1: Same Replay, Different Execution Style` | PASS | Real source excerpts only; regenerated focused code assets; detailed reasoning moved to transcript |
| 10 | `Result P1: A1 Is Still 3.30x Slower Than B0` | PASS | Bounded result table; short note only; methodology detail removed from slide |
| 11 | `Result P2: Bridge Tax Is Only Part Of The Gap` | PASS | Attribution now shown as chart instead of prose; one-sentence conclusion remains on slide |
| 12 | `Result P3: Nsight Supports A Launch-Structure Explanation` | PASS | Nsight evidence now shown as chart instead of prose; conclusion is explicit and short |

## GIF / Video Audit

- Before revision:
  - no dedicated performance GIF was embedded in the performance slides
- After revision:
  - `formal_slide/meeting_2026_04_01/gif/rope_perf_case_anchor.gif` is embedded on slide 8
  - size: `6,508,023` bytes
  - source GIF size: `26,028,370` bytes
  - both are below the `< 40 MB` requirement
  - the GIF is evidence-bearing, not decorative: it shows the rope replay case that the benchmark section studies
- PPTX embed check:
  - full deck contains embedded GIF media under `ppt/media/*.gif`
  - performance-only slice contains exactly one embedded GIF under `ppt/media/image1.gif`

## Code Evidence Audit

- `code_replay_semantics.png`
  - source: `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
  - excerpt lines: `185-193` and `202-208`
  - rendered excerpt length: `17` lines
  - highlighted lines: `5`
- `code_granular_profile.png`
  - source: `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`
  - excerpt lines: `768-780` and `800-802`
  - rendered excerpt length: `17` lines
  - highlighted lines: `5`
- Result:
  - both code excerpts satisfy the `<= 20` rendered-line requirement
  - both use Python syntax highlighting and monospace rendering
  - both are now large enough to serve as slide evidence instead of decorative screenshots

## What Moved Into `transcript.md`

- benchmark fairness caveats and same-case methodology
- controller-trajectory parity statement
- exact substep / physics-time context for the throughput table
- detailed A0/A1/B0 interpretation
- A3 / B1 attribution explanation with exact values
- detailed Nsight interpretation and the “launch structure, not collision” argument
- optimization implication after the Nsight result

## `todo_list.md` Consistency

No logic change was needed. The performance conclusion in `todo_list.md` already matched the revised slides:

- fair rope replay benchmark complete
- A1 still about `3.295x` slower than B0
- bridge tax is real but partial
- residual gap points to execution structure, not collision

## Generated Outputs

- full deck:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
- full transcript:
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/transcript.pdf`
- performance-only slice:
  - `tmp_vis/performance_analysis_20260401/bridge_meeting_20260401_performance_only_slides_8_12.pptx`
  - `tmp_vis/performance_analysis_20260401/bridge_meeting_20260401_performance_only_slides_8_12.pdf`
  - `tmp_vis/performance_analysis_20260401/transcript.md`
  - `tmp_vis/performance_analysis_20260401/transcript.pdf`

## Acceptance Summary

- Every revised performance slide is hypothesis-driven or conclusion-driven: PASS
- Slides remain in English: PASS
- Transcript remains Chinese with English terminology preserved: PASS
- Code evidence is real source code: PASS
- Each code excerpt is `<= 20` lines: PASS
- Highlighting stays within `<= 5` lines per excerpt: PASS
- Slides are readable in `15-20` seconds: PASS
- Detailed explanation moved into `transcript.md`: PASS
- GIF/video evidence is embedded where needed: PASS
- Embedded performance GIF is `< 40 MB`: PASS
- Revised section is more persuasive without becoming longer: PASS
