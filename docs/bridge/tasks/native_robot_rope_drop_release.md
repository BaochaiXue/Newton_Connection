# Task: Native Robot Rope Drop/Release Sanity Baseline

## Question

Can a simple native Newton Franka baseline release a rope, let it free-fall
under gravity, and visibly hit a real ground collider without the old
lift/push presentation complexity?

## Why It Matters

This is the stage-0 sanity baseline for the robot + rope workstream.

It separates three questions that were previously entangled:

- native robot integration
- semi-implicit rope dynamics
- gravity-driven drop with real ground contact

It is intentionally narrower than the final two-way-coupling demo.

## Current Status

- Recoil-fixed stage-0 baseline promoted under:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5`
- Matched drag-ON comparison run:
  - `results/native_robot_rope_drop_release/runs/20260331_232459_native_franka_recoilfix_drag_on_w5`
- The old lift-release path remains the historical reference
- The new milestone should be evaluated as its own evidence bundle, not as a
  continuation of the old lift/push story
- The current promoted run now satisfies the recoil-free acceptance target

## Code Entry Points

- Main script:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Shared helpers:
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
- Validation paths:
  - `scripts/validate_robot_rope_drop_release_physics.py`
  - `scripts/validate_native_robot_rope_drop_release_video.py`

## Canonical Commands

Canonical wrapper:

```bash
scripts/run_native_robot_rope_drop_release.sh \
  --slug recoilfix_drag_off_w5 \
  --no-apply-drag \
  --screen-width 1280 \
  --screen-height 720 \
  --render-fps 30 \
  --anchor-height 0.75 \
  --anchor-count-per-end 2 \
  --auto-set-weight 5.0 \
  --drop-approach-seconds 0.15 \
  --drop-support-seconds 0.25 \
  --drop-release-seconds 0.05 \
  --drop-freefall-seconds 1.00 \
  --ik-target-blend 0.35 \
  --gripper-hold 0.012 \
  --drop-preroll-settle-seconds 2.0 \
  --pre-release-settle-damping-scale 8.0 \
  --rope-line-width 0.04
```

Underlying demo entry point:

```bash
python Newton/phystwin_bridge/demos/demo_robot_rope_franka.py \
  --task drop_release_baseline \
  --render-mode presentation
```

## Required Artifacts

- `summary.json`
- `physics_validation.json`
- `ffprobe.json`
- `contact_sheet.png`
- `event_sheet.png`
- `final_debug.mp4`
- `final_presentation.mp4`
- `verdict.md`

## Success Criteria

- native Newton Franka is visible in the scene
- the rope is supported before a clear release time
- after release, the rope is dynamically free and gravity-driven
- the rope hits a real physical ground collider
- the 1:1 presentation render is readable and visually sane
- drag on/off A/B validation is recorded
- the run does not visually read as a fake tabletop or a slow-motion replay

## Open Questions

- For the current recoil-fixed 5 kg baseline, drag OFF and drag ON both keep
  the early fall gravity-like and the A/B difference is minor; future variants
  may still choose OFF for simplicity or ON for slightly softer post-impact
  behavior.
- Is the release mechanism simple enough that the robot no longer dominates
  the story after `t_release`?

## Related Pages

- [video_presentation_quality.md](./video_presentation_quality.md)
- [robot_deformable_demo.md](./robot_deformable_demo.md)
