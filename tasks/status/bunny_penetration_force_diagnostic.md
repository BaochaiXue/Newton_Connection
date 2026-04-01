# Status: Bunny Penetration Force Diagnostic

## 2026-04-01

- Reopened the task under a stricter meeting spec.
- Explicitly marked the old accepted full-process synchronized package as
  historical rather than final for meeting visualization.
- Re-scoped the main deliverable to:
  - self-collision OFF
  - `box_control`
  - `bunny_baseline`
  - real-time `2 x 2`
  - all currently colliding cloth mass nodes
- Updated the repo-native task page, spec, plan, and implement runbook so the
  new deliverable is the source of truth rather than an add-on note.

## Current Technical State

- Historical trigger/full-process force diagnostics already exist.
- Existing board/render code also exists, but it is still short of the stricter
  spec in at least these ways:
  - main board currently follows geometry-contact membership instead of the
    force-active collision set
  - the current board path does not yet save a formal per-frame detector bundle
    as a promoted artifact
  - board-level validation is not yet strict enough for the new semantics
  - the old docs still overstated the historical accepted run as final

## Next Step

- harden detector persistence
- harden board semantics
- extend validator coverage
- produce a fresh promoted run under a new
  `*_realtime_allcolliding_2x2_v1` directory
