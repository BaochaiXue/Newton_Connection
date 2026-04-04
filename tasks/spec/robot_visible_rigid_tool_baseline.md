# Spec: robot_visible_rigid_tool_baseline

## Goal

Build a visually honest robot-mounted rigid-tool baseline where the visible tool
is the actual physical contactor for a readable tabletop rope push.

## Scope

- attach a visible rigid tool to the native Franka in the bridge/demo layer
- make the physical tool geometry and visible tool geometry match
- preserve truthful rope thickness
- produce a full fail-closed video review bundle

## Non-Goals

- proving robot-table physical blocking
- full two-way coupling
- direct finger-contact claim
- changing `Newton/newton/`

## Constraints

- tool must be visible and believable
- no hidden helper
- no fake-thin render on top of a much fatter collider
- no stand-off push impression

## Outputs

- new task chain
- new canonical wrapper for the visible-tool baseline
- candidate bundles under a dedicated result root
- tool truth diagnostics and full-video review

## Done When

- visible tool is clearly the actual physical contactor
- rope reacts only after visible tool contact
- no fake-geometry appearance remains
- no hidden helper is present
- full video bundle and review pass conservatively
