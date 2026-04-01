# Performance Rewrite Audit — 2026-04-01

## Scope

This audit covers the TODO 2 / performance-profiling block in the
`2026-04-01` meeting deck.

Source of truth:

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- `formal_slide/meeting_2026_04_01/transcript.md`

Target slide block after rewrite:

- Slides `8-12`

## Main Problems In The Previous Version

### 1. Core claims were sometimes proved with the wrong code layer

Bad pattern:

- using our own wrapper / benchmark / replay harness as if it proved a Newton core or PhysTwin core runtime idea

Why this failed:

- wrapper code can prove fairness setup
- wrapper code cannot prove core execution structure
- the professor-facing question is about rope-case performance logic, not our harness plumbing

### 2. The research order was not explicit enough

The intended logic is:

1. establish a fair same-case rope benchmark
2. measure the throughput gap
3. explain why the gap remains
4. only then discuss optimization implication

Previous slides partially mixed:

- fairness setup
- runtime explanation
- optimization direction

without making that order explicit enough.

### 3. The previous performance section contained evidence with the wrong level

Wrong evidence level:

- our own wrapper / benchmark code for core claims
- self-made data charts for the main bottleneck story

Required evidence level:

- Level 1: Newton core / PhysTwin core source
- Level 2: our harness only for methodology/fairness
- Level 3: system/timing evidence
- Level 4: rope GIF

### 4. Several lines sounded like internal production notes

Examples removed or downgraded:

- internal benchmark-process narration
- “page-purpose” writing
- shorthand labels such as `bridge tax on`
- implementation shorthand that a professor would not decode

### 5. Transcript detail was too uneven

The new source-proof slides required a stronger transcript treatment:

- explicit file + rough line range
- code block
- `What / Why / Risk`
- line-by-line physical / numerical explanation

## Slides Fully Restructured

- `Slide 8`
  - from a benchmark-method slide into a benchmark question slide
- `Slide 9`
  - from a generic execution-style code page into a physics-intent source-proof page
- `Slide 10`
  - same throughput table logic retained, but wording was rewritten into professor-readable English
- `Slide 11`
  - from a short bottleneck-summary page into a core execution-structure source-proof page
- `Slide 12`
  - from a loose bottleneck-summary page into a clear research-order takeaway page

## Wrapper Citations That Were Downgraded

Removed as core proof:

- bridge-local replay / benchmark wrapper logic
- wrapper-level argument parsing or control-mode plumbing

Allowed after rewrite only as methodology context:

- fairness setup
- replay identity
- benchmark bookkeeping

## Core Files Now Used For The Performance Argument

Newton core:

- `Newton/newton/newton/_src/solvers/solver.py`
- `Newton/newton/newton/examples/cable/example_cable_pile.py`

PhysTwin core:

- `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`

## Content Moved Out Of Main Slides

Moved to transcript:

- detailed fairness explanation
- why rope case is a weak-collision diagnostic
- exact substep / trajectory counts
- line-by-line code analysis
- `What / Why / Risk`
- caveats about “same formula” versus “closely comparable semi-implicit rope update intent”

Not kept on main slides:

- internal QA wording
- page-purpose narration
- self-made performance charts
- wrapper code as proof of core behavior

## Transcript 1:50 Focus

The strict 1:50 rewrite effort was concentrated on:

- `Slide 9`
  - Newton core semi-implicit update
  - PhysTwin spring force + velocity update
- `Slide 11`
  - Newton rope-side graph-capture / substep loop structure
  - PhysTwin graph replay path

These are the pages where the code actually participates in the argument, so
they received the deepest `What / Why / Risk` treatment.
