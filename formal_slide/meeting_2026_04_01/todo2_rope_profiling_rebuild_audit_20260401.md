# TODO 2 Rope Profiling Rebuild Audit — 2026-04-01

## Scope

Audit target:

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- `formal_slide/meeting_2026_04_01/transcript.md`
- `results/rope_perf_apples_to_apples/`

Section under review:

- TODO 2 / rope-case profiling section only

## 1. Why The Old Profiling Section Did Not Explain Its Value To The Real Viewer

The old section jumped too quickly into the no-render benchmark without first
answering the practical audience question:

- what part of the current rope viewer is actually slow?
- is rendering the main reason?
- why should the audience care about a no-render benchmark?

That made the whole section feel detached from the visible real viewer.

## 2. Which Pages Made The Experiment Hard To Understand

- Old Slide 8:
  - it locked fairness correctly, but it did not first explain why this
    benchmark mattered to the viewer
- Old Slide 9:
  - it cited physical-intent code, but it did not define E1/A0/A1/B0 in plain
    language
- Old Slides 10-14:
  - they used shorthand-heavy reasoning and assumed the audience already knew
    what A0, A1, B0, bridge tax, and launch structure meant

## 3. Which Terms Were Internal Shorthand And Had To Be Removed From Slides

These were identified as meeting-hostile shorthand:

- `bridge tax`
- `tax reduced`
- `launch-dominated`
- `graph-launch-dominated`
- `execution structure, not collision`

They were replaced on slides by plain-language phrases:

- `controller replay overhead`
- `render ON vs render OFF`
- `many separated launches remain on the Newton side`
- `PhysTwin uses graph-based replay`
- `within this controlled rope benchmark, the residual gap is more consistent with runtime organization`

## 4. Which Transcript Sections Did Not Sound Like Normal Speech

The previous transcript failures were mostly in Slides 10-14:

- it read like expanded internal notes
- it stacked shorthand terms instead of spoken explanations
- some pages skipped the key sentence:
  - what question this page answers
  - what evidence is being shown
  - what conclusion the audience should carry away

The rebuild requirement was therefore:

- each page must explain question -> evidence -> conclusion -> viewer value ->
  limitation in full sentences

## 5. Which Earlier Conclusions Were Stronger Than The Evidence

The following old claims were too aggressive for the evidence level:

- any wording that implied launch structure was already fully proven
- any wording that made collision globally irrelevant
- any wording that implied full physics parity

The corrected claim boundary is:

- in this controlled rope replay benchmark,
- after replay-overhead reduction,
- the residual gap is more consistent with runtime organization than with
  replay overhead alone

This is deliberately weaker and more honest than a universal causality claim.

## 6. Which New Experiments Were Needed

The earlier benchmark matrix already covered:

- Newton A0/A1 throughput
- Newton A2/A3 attribution
- PhysTwin B0/B1 headless replay
- Nsight A1/B0

But it still lacked a viewer-facing row.

So the rebuild added:

- E1 = Newton real viewer end-to-end on the same rope replay, render ON,
  visible `ViewerGL`

Why E1 was necessary:

- without it, the audience could not tell whether the no-render benchmark was
  diagnosing a real viewer bottleneck or just an abstract simulator benchmark

## Updated Evidence Chain

The rebuilt section now uses this order:

1. real viewer relevance
2. controlled rope benchmark definition
3. main numbers
4. what A0 -> A1 isolates
5. what the residual gap suggests and does not prove
6. what to optimize next for the real viewer

## Slide-By-Slide Fix Plan Implemented

1. P1
   - add E1 visible-viewer measurement
   - show render ON vs render OFF relation
   - explain why no-render replay is still relevant to the viewer
2. P2
   - define E1 / A0 / A1 / B0 in plain language
   - make same-case fairness explicit
3. P3
   - keep only the load-bearing throughput table
   - separate practical viewer row from simulator-only rows
4. P4
   - define controller replay overhead directly
   - explain A0 -> A1 without shorthand
5. P5
   - use Newton core staged-step code plus PhysTwin core graph-capture code
   - pair them with honest Nsight wording
6. P6
   - connect the whole profiling chain back to the next real-viewer
     optimization step

## Expected Outcome

After this rebuild, a normal meeting audience should be able to answer in
2-3 minutes:

- what experiment was run
- why it matters to the real viewer
- how far Newton is from PhysTwin on the same rope replay
- what that gap suggests, and what it still does not prove
