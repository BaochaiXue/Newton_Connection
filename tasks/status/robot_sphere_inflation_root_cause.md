# Status: robot_sphere_inflation_root_cause

## Current State

- Completed
- Ranked mechanism report and supporting diagnostics are now on disk

## Last Completed Step

- Wrote the ranked root-cause report and supporting diagnostics from current
  c12/c15/c16/c19/c20 direct-finger histories plus the promoted c08 visible-tool
  control

## Next Step

- Use the ranked conclusion to guide the next honest path:
  - direct-finger re-certification only after reference geometry and laydown/path
    alignment are corrected
  - keep the promoted visible-tool baseline as the current conservative honest
    control
  - do not treat sphere inflation as a physical fix

## Guardrail

- Do not silently relabel the accepted tabletop finger baseline
- Do not use the visible-tool baseline as a dodge instead of answering the
  sphere-inflation mechanism question
- Do not touch `Newton/newton/`

## Ranked Conclusion

- Primary root cause: `H1 wrong contact reference point` combined with `H3 XY
  trajectory / laydown miss`
- Secondary contributors:
  - `H4 rope physical thickness smaller than the old mental model`
  - `H2 stale Z-stack assumptions`
  - `H5 proxy semantics can mislead diagnostics if over-trusted`
  - `H6 controller semantics matter for stronger physics claims, but are
    secondary for this specific question`

## ee_contact_radius Decision

- `ee_contact_radius` should remain available only as a diagnostic/proxy knob.
- It is **not** a real robot contact geometry parameter.
- It is **not** valid as contact proof.
- It is **not** allowed as a final acceptance surface.
- If future tabletop claims depend on it again, that should be treated as a
  regression.

## Key Evidence

- In promoted c12, the tabletop command target remains gripper-center based.
- The mean target -> nearest finger-box surface distance is about `0.0424 m`,
  while the nominal proxy effective radius is `0.033 m`.
- At first actual finger-box contact in c12, gripper-center -> actual contact
  surface distance is about `0.0780 m`:
  - XY component: `0.0489 m`
  - Z component: `0.0609 m`
- True-size rope contact timing changes strongly with laydown/base alignment,
  not sphere size:
  - c15: `4.3355 s`
  - c16: `3.63515 s`
  - c19: `1.23395 s`
  - c20: `2.83475 s`
- The promoted visible-tool control c08 reaches honest tool-first contact at
  `1.7342 s` with `multi_frame_standoff_detected = false`, proving the same
  rope/tabletop context can be hit honestly without sphere fiction when the
  contactor is explicit.

## Durable Surfaces

- [why_robot_spheres_need_inflation_ranked_report.md](/home/xinjie/Newton_Connection/diagnostics/why_robot_spheres_need_inflation_ranked_report.md)
- [robot_sphere_geometry_inventory.md](/home/xinjie/Newton_Connection/diagnostics/robot_sphere_geometry_inventory.md)
- [finger_vs_proxy_geometry_report.md](/home/xinjie/Newton_Connection/diagnostics/finger_vs_proxy_geometry_report.md)
- [contact_reference_offset_report.md](/home/xinjie/Newton_Connection/diagnostics/contact_reference_offset_report.md)
- [xy_reachability_report.md](/home/xinjie/Newton_Connection/diagnostics/xy_reachability_report.md)
