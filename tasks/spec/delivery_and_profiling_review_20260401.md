# Spec: delivery_and_profiling_review_20260401

> status: historical
> canonical_replacement: none
> owner_surface: `delivery_and_profiling_review_20260401`
> last_reviewed: `2026-04-01`
> notes: Historical one-off review spec; do not reuse as a live task surface.

## Goal

Produce a strict review of the current meeting-facing deliverables and the
current rope profiling plan, using in-repo evidence rather than memory.

## Non-Goals

- Changing Newton core code under `Newton/newton/`
- Re-recording demos in this task
- Rebuilding the slide deck unless needed to inspect structure
- Running a new long profiling campaign

## Inputs

- `docs/bridge/tasks/delivery_and_profiling_review_20260401.md`
- `formal_slide/meeting_2026_04_01/`
- `results/native_robot_rope_drop_release/`
- `results/rope_perf_apples_to_apples/`
- `docs/bridge/tasks/video_presentation_quality.md`
- `docs/bridge/tasks/interactive_playground_profiling.md`

## Outputs

- evidence-backed review conclusions
- list of visualization defects or risks in the promoted demo outputs
- profiling blind spots and suggested next cuts

## Constraints

- Do not modify `Newton/newton/`
- Treat user-edited dirty files as read-only unless a change is essential
- Prefer existing validation and QA artifacts over ad hoc interpretation

## Done When

- slides, transcript, and demo artifacts have all been inspected
- profiling plan is compared against the current benchmark evidence
- the final response includes concrete conclusions and references
