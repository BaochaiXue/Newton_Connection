# Status: robot_rope_true_size_recalibration

## Current State

- Active
- Goal is to recover a natural laydown and visible true finger contact after
  shrinking the rope's physical radius
- `c12` remains the committed authoritative tabletop hero; true-size work is
  still exploratory and must not update `results_meta/` unless it truly
  replaces `c12`

## Last Completed Step

- Re-read the current tabletop hero control plane, audited the accepted `c12`
  route against the new `0.1x` physical-radius default, and completed the
  first bounded sweep set `c15/c16/c17`.
- Added a new `tabletop_shallow_curve` laydown mode and started coupled repair
  candidate `c18` with:
  - `--particle-radius-scale 0.1`
  - `--tabletop-initial-pose tabletop_shallow_curve`
  - `--tabletop-preroll-settle-seconds 3.5`
  - `--tabletop-preroll-damping-scale 2.5`
  - `--tabletop-robot-base-offset -0.56 -0.20 0.08`

## Next Step

- Finish `c18`, inspect full videos, and decide whether the next bounded repair
  should continue with base-pose retuning or move to explicit joint-waypoint
  recalibration.

## Latest Findings

- Current repo default drift is real:
  - demo default `--particle-radius-scale` is now `0.1`
  - wrapper still carries the old `c12` joint-trajectory geometry and old
    tabletop pose assumptions
- Accepted controller path is still `joint_trajectory`, so most tabletop
  world-space clearance arguments are not the active control surface for the
  promoted path.
- Primary coupled regression board so far:
  - `tabletop_curve` is stale for `0.1x` rope and over-shapes the laydown
  - the old joint-trajectory path no longer meets the smaller rope early enough
  - XY and Z both drifted; this is not a proxy-only problem
- Candidate comparison:
  - `c15 (0.1x)`:
    - laydown reads too hand-shaped and thin
    - `actual_finger_box_first_contact_time_s = 4.3355`
    - validator fail
  - `c16 (0.25x)`:
    - slightly better contact than `c15`, but causal ambiguity comes back
    - `actual_finger_box_first_contact_time_s = 3.63515`
    - validator fail
  - `c17 (0.5x)`:
    - stronger rope response, still too late for accepted quality
    - `actual_finger_box_first_contact_time_s = 3.56845`
    - validator fail
  - `c18 (0.1x + shallow curve + softer longer preroll + lower/closer base)`:
    - first presentation pass shows a visibly more natural laydown than `c15`
    - presentation summary shows `actual_finger_box_first_contact_time_s = 3.2683`
    - still not enough to claim success; full bundle and full-video review are
      pending
  - `c19 (0.1x + shallow curve + base -0.54 -0.20 0.06)`:
    - clean presentation summary is a major reachability improvement:
      - `actual_finger_box_first_contact_time_s = 1.23395`
      - `first_contact_phase = approach`
      - `contact_duration_s = 2.3345`
      - `contact_onset_report` says actual finger-box contact at frame `37`,
        rope lateral motion at frame `42`, rope deformation at frame `43`
    - first-frame laydown and early-contact keyframes are visibly better than
      `c15/c16/c18`
    - however, the full bundle still fails because manual review is still the
      template and because cross-view timing drift remains present
    - `c19` also crossed a code-edit window, so it is being treated as a
      parameter-discovery run rather than a promotable clean authority run
  - `c20_clean`:
    - reruns the exact `c19` parameter set after the summary-only code patch so
      the bundle provenance is clean

## Diagnosis Summary

- Laydown:
  - `tabletop_curve` uses fixed `arch/s-curve` magnitudes that become too
    aggressive once physical radius shrinks to `0.1x`
  - `tabletop_shallow_curve` is the current better direction
- Reachability:
  - the accepted `c12` hard-coded joint path is now stale for the smaller rope
  - first contact moved from `1.6675s` in `c12` to `4.3355s` in `c15`
  - `c18` recovers some of that loss, but still contacts too late
  - `c19` shows that a bounded base-pose change can recover early approach
    contact without reverting to thick renders or proxy-only proof
- Proof surface:
  - actual finger-box contact remains the governing proof surface
  - no evidence supports reverting to `finger_span` as primary proof
- Cross-view determinism:
  - repeated reruns with the same parameters do not produce identical contact
    timing across `presentation / debug / validation`
  - this variance already existed in `c15/c16/c17/c18`; `c19` makes it more
    visible because the presentation run lands much earlier contact than the
    debug run
  - until the clean rerun (`c20_clean`) is inspected, `c19` should not be used
    as a promoted authority surface
- Authority:
  - keep `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
    unchanged unless a new true-size candidate fully replaces `c12`

## Blocking Issues

- No infrastructure blocker.
- Main technical blocker is still coupled geometry mismatch between:
  - smaller physical rope
  - tabletop laydown
  - fixed joint-trajectory contact line

## Artifact Paths

- current accepted baseline:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
- true-size candidates:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260402_140811_physradius0p1_c15/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_000517_physradius0p25_c16/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_002700_physradius0p5_c17/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_004718_true0p1_shallowcurve_bz008_by020_c18/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_005533_true0p1_shallowcurve_bx054_by020_bz006_c19/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_010241_true0p1_shallowcurve_bx054_by020_bz006_c20_clean/`
- diagnosis board:
  - `diagnostics/robot_rope_true_size_recalibration_board.md`
