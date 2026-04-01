# Task: Robot + Deformable Demo

## Question

Can a native Newton robot asset actively interact with a PhysTwin-loaded
deformable object in a way that is visually and quantitatively defendable in a
meeting?

## Why It Matters

This is the clearest downstream bridge claim. The point is not just that a
deformable object moves in Newton, but that a robot can manipulate it through a
native Newton interaction path.

## Current Status

- Canonical best run selected.
- The proxy robot demo has been retired; the canonical mainline is now
  `demo_robot_rope_franka.py`.
- The authoritative result bundle is now:
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`
- The current native Franka baseline now produces the full review bundle:
  - `final.mp4`
  - `summary.json`
  - `ffprobe.json`
  - `contact_sheet.png`
  - `event_sheet.png`
  - `validation.json`
  - `verdict.md`
- The previous summary/contact mismatch was fixed by switching the robot-contact
  metric to a finger-span proxy instead of a gripper-center-only proxy.
- Presentation framing is now more explicit:
  - hero camera defaults to the rope-contact region
  - a validation camera preset is stored in the run summary
  - an earth-tone ground grid makes the support plane legible
  - stage/anchor support shapes are slightly larger in presentation mode
  - latest validation run:
    - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`
- The latest tuning keeps the native Franka + semi-implicit path, but adds
  phase-gated drag on `pre_approach + release_retract` to reduce abnormal motion
  while preserving the stable release timing.
- A narrower stage-0 drop/release sanity baseline now exists separately under
  `docs/bridge/tasks/native_robot_rope_drop_release.md`; do not mix that
  evidence into this lift-release claim.

## Code Entry Points

- Main script:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Presentation references:
  - `Newton/phystwin_bridge/demos/demo_two_ropes_ground_contact.py`
  - `formal_slide/meeting_2026_03_25/build_meeting_20260325.py`
- Shared bridge helpers:
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`

## Claim

> A native Newton robot asset can actively interact with a PhysTwin-loaded
> deformable object, and the interaction is visibly and measurably two-way.

For the current scope, this should be defended through the rope path first.

## Scope

### Required deliverables

- One reproducible native robot script.
- One hero `mp4`.
- One `gif`.
- One `summary.json`.
- One PPT slide whose title is the claim, with one hero frame and three
  supporting metrics.

### Non-goals

- Exact PhysTwin self-collision replication.
- Bunny penetration repair.
- MPM two-way coupling.
- Realtime as a hard blocker.
- Expanding the same task to cloth/sloth/bunny simultaneously.

## Canonical Command

Run the native Franka baseline first:

```bash
scripts/run_robot_rope_franka.sh
```

## Required Artifacts

- Summary JSON:
  - `first_contact_time_s`
  - `contact_duration_s`
  - `rope_com_displacement_m`
  - `first_contact_frame`
  - `contact_active_frames`
  - `min_clearance_min_m`
  - `contact_proxy_mode`
  - `contact_peak_proxy`
- Video:
  - fixed-view `mp4`
  - meeting-usable `gif`
- Presentation:
  - one slide with the claim in the title
  - one GIF or hero video asset
  - 2-4 numbers pulled directly from the summary

## Acceptance

### Minimum acceptance

- Script runs to completion without crash or NaN.
- `first_contact_frame` is not `null`.
- `contact_active_frames >= max(10, 1% * frames)`.
- `rope_com_displacement_m >= 0.02`.
- Output includes fixed-view video plus summary metrics plus validation bundle.
- The demo can be explained in 15 seconds.
- The manual video verdict is explicitly recorded as PASS.

### Stretch target

- The same configuration succeeds repeatedly.
- `rope_com_displacement_m >= 0.05`.
- The PPT version is strong enough to stand as a result slide, not just an
  appendix clip.

## Definition Of Done

### DoD-A: Technical baseline

- Native Franka script runs.
- Contact happens.
- Rope visibly responds.
- Summary JSON is populated with usable metrics that match the visible contact.

### DoD-B: Meeting-grade baseline

- The native Franka version is the canonical demo.
- The PPT slide, hero frame, and numbers tell the same story.
- The explanation is explicit about the claim boundary:
  native robot asset interaction baseline first, deeper robot feedback claims
  only after evidence exists.
- The result bundle is promoted under `results/robot_deformable_demo/`.

### DoD-C: Enhancement

- Better camera / scene context.
- Hero/validation camera presets are documented in the output summary.
- Ground/support framing is explicit enough that the rope no longer reads as
  floating in empty space.
- More natural robot start pose.
- Stronger visual staging without changing the core claim.

## Open Questions

- Should cloth be a follow-on task after the rope line is fully defendable?
- When do we promote this from “native interaction baseline” to a stronger
  “robot feels deformable resistance” claim?

## Related Pages

- [video_presentation_quality.md](./video_presentation_quality.md)
- [slide_deck_overhaul.md](./slide_deck_overhaul.md)
- [native_robot_rope_drop_release.md](./native_robot_rope_drop_release.md)
