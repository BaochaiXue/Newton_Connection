# Geometry Truth Inventory

Last updated: 2026-04-04

## Current Direct-Finger Tabletop Baseline

- Robot asset:
  - native Newton Franka imported from `fr3_franka_hand.urdf`
  - entrypoint: [demo_robot_rope_franka.py](/home/xinjie/Newton_Connection/Newton/phystwin_bridge/demos/demo_robot_rope_franka.py)
- Actual physical finger geometry:
  - URDF-imported multi-box finger colliders
  - not spheres
- Visible finger geometry:
  - native Franka visual mesh
- Truth rule:
  - accepted proof surface is actual finger-box contact, not `gripper_center`,
    `left_finger`, `right_finger`, or `finger_span` proxy semantics

## Current Visible-Tool Baseline

- Robot-side contactor:
  - visible red capsule/crossbar attached to `fr3_link7`
- Actual physical contactor:
  - same capsule shape parameters as the visible render path
- Current promoted dimensions:
  - radius: `0.0055 m`
  - half-height: `0.018 m`
  - local offset: `(0.0, -0.034, 0.186)`
  - axis: `x`
- Truth rule:
  - visible-tool render dimensions must match the actual capsule collider
  - same-rollout hero/debug/validation is already required

## Table Geometry

- Native tabletop physical blocker:
  - box shape with
    - `table_top_z`
    - `table_hx`
    - `table_hy`
    - `table_hz`
- Presentation rule:
  - visible tabletop top must match the real physical table box
  - decorative floor/pedestal/legs may exist, but must not be mistaken for the
    actual blocking surface

## Rope Geometry

- Rope physical contact thickness must stay aligned with render thickness in any
  final pass.
- For the stronger blocking task, Stage 0 will omit the rope entirely.
- When Stage 1 reintroduces the rope, the render thickness must again match the
  physical rope contact thickness; no thin render / fat physics mismatch is
  allowed.

## Proxy / Diagnostic Geometry

- `ee_contact_radius`
  - diagnostic only
  - may affect overlays and proxy-clearance reports
  - does **not** change the real finger collider geometry
  - not valid as contact proof
  - not allowed as a final acceptance surface

## Planned Stage-0 Honest Geometry

- Simplest honest robot-side contactor:
  - visible rigid capsule/crossbar mounted on the Franka end-effector
- Why:
  - easier to audit than bare finger mesh vs multi-box collider alignment
  - render mesh and collider can be generated from the same dimensions
  - contact patch is easier to read in hero/debug/validation views

## Current Geometry-Truth Risks To Watch

- direct-finger path:
  - visual mesh is not identical to the box-collider decomposition, so
    validation overlays are required if direct finger contact is claimed
- physical-blocking path:
  - any rerender that does not come from the same rollout history is a fail
- Stage 1 rope reintegration:
  - rope render thickness and actual rope contact thickness must remain aligned
