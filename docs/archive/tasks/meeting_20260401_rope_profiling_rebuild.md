# Task: Meeting 2026-04-01 Rope Profiling Rebuild

> status: historical
> canonical_replacement: `docs/bridge/tasks/rope_perf_apples_to_apples.md`
> owner_surface: `meeting_20260401_rope_profiling_rebuild`
> last_reviewed: `2026-04-01`
> review_interval: `90d`
> update_rule: `Do not update for current work; keep only as the historical record of the 2026-04-01 profiling-section rewrite.`
> notes: Historical one-off meeting rebuild record. Current benchmark authority lives under `rope_perf_apples_to_apples`; current meeting-story maintenance lives under `slide_deck_overhaul`.

## Question

Can the TODO 2 profiling section in the 2026-04-01 meeting deck be rebuilt
into a real-viewer-relevant, rope-case-only story that ordinary meeting
audiences can follow in 2-3 minutes?

## Why It Matters

The previous profiling section already had the right high-level order, but it
still failed the meeting test:

- the audience could not tell what experiment was being run
- the connection to the real rope viewer was weak
- A0/A1/B0 and earlier shorthand terms were not self-explanatory
- some claims sounded stronger than the cited evidence

This rebuild must make the profiling section presentation-ready without
weakening the scientific boundary.

## Required Questions To Answer

1. What exactly is the profiling experiment measuring?
2. Why is that experiment relevant to the real rope viewer?
3. Under the same rope replay benchmark, how far is Newton from PhysTwin?
4. What does the measured gap suggest, and what does it not prove?

## Scope

- Only the rope-case profiling section in:
  - `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/todo_list.md`
- May supplement rope experiments under:
  - `results/rope_perf_apples_to_apples/`
- May update profiling support scripts under:
  - `scripts/`

## Non-Goals

- Reworking the robot or bunny sections unless slide numbering forces it
- Modifying Newton core under `Newton/newton/`
- Replacing the apples-to-apples rope benchmark with a robot/contact-heavy case

## Required Experiment Matrix

- E1: Newton rope real-viewer end-to-end, render ON
- E2: Newton same rope replay, render OFF
- E3: Newton A0 vs A1 to isolate controller replay overhead
- E4: PhysTwin same-case headless replay
- E5: Nsight / system evidence only if needed to explain the residual gap

## Success Criteria

- profiling section becomes understandable without prior shorthand knowledge
- real-viewer relevance is explicit, not implied
- core claims cite Newton core / PhysTwin core or honest system evidence
- transcript reads like normal spoken explanation
- deck is regenerated successfully

## Related Pages

- [rope_perf_apples_to_apples.md](../../bridge/tasks/rope_perf_apples_to_apples.md)
- [interactive_playground_profiling.md](../../bridge/tasks/interactive_playground_profiling.md)
- [current_status.md](../../bridge/current_status.md)
