# Robot Sphere Geometry Inventory

Last updated: 2026-04-04

## What The Actual Physical Finger Geometry Is

- The native Franka hand/finger physics comes from the URDF imported in
  [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py).
- The actual rope-contact-capable finger geometry used in the tabletop task is
  **box colliders** on:
  - `fr3/fr3_leftfinger`
  - `fr3/fr3_rightfinger`
- Those boxes are discovered at runtime by
  `_finger_box_entries(...)` in
  [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py).
- The accepted tabletop finger baseline now uses these **actual finger boxes**
  as the primary proof surface, not `finger_span`.

## What “Sphere Inflation” Means In Code Terms

There are two distinct meanings:

1. **Diagnostic/proxy sphere inflation**
   - parser arg: `--ee-contact-radius`
   - default in demo: `0.055`
   - used by `_gripper_contact_proxy_radii(...)`
   - produces point/sphere proxies for:
     - `gripper_center`
     - `left_finger`
     - `right_finger`
     - `finger_span`
   - this is the main “sphere-like” semantic in the direct-finger tabletop path

2. **Actual visible/physical rigid tool geometry**
   - parser args:
     - `--visible-tool-radius`
     - `--visible-tool-half-height`
     - `--visible-tool-offset`
     - `--visible-tool-axis`
     - `--visible-tool-body`
   - this is a real physical capsule in the Newton model, not a diagnostic
     proxy
   - used in the promoted visible-tool baseline

## Quantities That Actually Affect The Scene / Contact Semantics

These change the actual simulated geometry or contact-relevant scene:

- `--particle-radius-scale`
  - rescales the rope’s **physical** particle/contact radius before model build
- finger box colliders from the imported Franka URDF
- visible tool capsule when `--visible-tool-mode short_rod`
- tabletop placement / reachability stack:
  - `--tabletop-robot-base-offset`
  - `--tabletop-push-start-offset`
  - `--tabletop-push-contact-offset`
  - `--tabletop-push-end-offset`
  - `--tabletop-retract-offset`
  - `--tabletop-approach-clearance-z`
  - `--tabletop-contact-clearance-z`
  - `--tabletop-push-clearance-z`
  - `--tabletop-retract-clearance-z`
  - `--tabletop-ee-offset-z`
  - `--tabletop-initial-pose`
  - preroll settle params

## Quantities That Are Diagnostic / Review Semantics

These do **not** change the actual simulated rope-vs-robot contact geometry:

- `--ee-contact-radius`
  - only affects proxy-radius based clearance calculations and debug overlays
- `_min_gripper_proxy_clearance(...)`
  - diagnostic only
- `gripper_center`, `left_finger`, `right_finger`, `finger_span`
  - proxy contact points / segment only
- `contact_proxy_mode`, `contact_proxy_counts`, `contact_peak_proxy`
  - summary/reporting semantics
- debug spheres shown in render path
  - `ee_target`
  - `gripper_center`
  - finger tip markers

## Render-Only Thickness Surfaces

These affect appearance but not physical rope contact:

- `--particle-radius-vis-scale`
- `--particle-radius-vis-min`
- `--rope-line-width`

The accepted remote-interaction truth fix already established that rope render
thickness must stay aligned with rope physical thickness for honest contact
reading.

## Wrapper Overrides That Matter

- [run_robot_rope_franka_tabletop_hero.sh](/home/xinjie/Newton_Connection/scripts/run_robot_rope_franka_tabletop_hero.sh)
  hard-codes:
  - `--tabletop-control-mode joint_trajectory`
  - `--tabletop-ee-offset-z 0.22`
  - `--tabletop-contact-clearance-z 0.010`
  - `--tabletop-push-clearance-z 0.008`
  - `--rope-line-width 0.024`

- [run_robot_visible_rigid_tool_baseline.sh](/home/xinjie/Newton_Connection/scripts/run_robot_visible_rigid_tool_baseline.sh)
  now hard-codes:
  - `--particle-radius-scale 0.1`
  - `--rope-line-width 0.006`
  - visible-tool capsule geometry on `link7`
  - debug/validation rerender from the same presentation rollout history

## Bottom Line

In the direct-finger rope case, “sphere inflation” is currently **not** an
actual physical finger-geometry inflation in the scene.

It is primarily:

- a **proxy/diagnostic sphere radius** around gripper/finger points
- plus, historically, a way to make near-miss trajectories look like contact
  in metrics or debug reasoning

The mechanism question is therefore not “why the physical robot needs huge
spheres,” but “what geometric/control mismatch those inflated proxy spheres
were compensating for.”
