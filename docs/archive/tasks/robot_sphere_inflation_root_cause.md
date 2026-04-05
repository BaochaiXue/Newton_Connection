> status: historical
> canonical_replacement: none
> owner_surface: `robot_sphere_inflation_root_cause`
> last_reviewed: `2026-04-05`
> review_interval: `60d`
> update_rule: `Historical record only; update only if its replacement or historical scope needs clarification.`
> notes: Historical mechanism study moved out of the active task index after the ranked conclusion stabilized.

# Task: Why Robot Spheres Need Inflation In The Rope Case

## Question

What error term were inflated robot spheres actually compensating for in the
tabletop rope case?

This task must distinguish between:

- wrong contact reference geometry
- stale tabletop Z-stack
- XY path miss
- stale rope-thickness mental model
- misleading proxy semantics
- controller/path semantics that make sphere inflation act like a workaround

## Why It Matters

“Bigger spheres work” is not a mechanism explanation.

This task matters because the project now has:

- an accepted direct-finger tabletop baseline
- an accepted visible-tool intermediary baseline
- a blocked stronger physical-blocking follow-on

To decide whether direct-finger re-certification is honest, we need to know
whether sphere inflation was:

- a real physical need
- a proxy workaround
- or a symptom of stale geometry/control assumptions

## Claim Boundary

This task does **not** claim a better demo by itself.

It only passes if it delivers:

- a ranked, evidence-backed root-cause story
- disambiguating experiments
- an honest recommendation for the next step

## Required Outputs

- `diagnostics/robot_sphere_geometry_inventory.md`
- `diagnostics/finger_vs_proxy_geometry_report.md`
- `diagnostics/finger_vs_proxy_clearance_timeseries.csv`
- `diagnostics/finger_vs_proxy_contact_onset_report.json`
- `diagnostics/contact_reference_offset_report.md`
- `diagnostics/contact_reference_timeseries.csv`
- `diagnostics/z_stack_report.md`
- `diagnostics/z_stack_timeseries.csv`
- `diagnostics/xy_reachability_report.md`
- `diagnostics/xy_miss_distance_timeseries.csv`
- `diagnostics/rope_thickness_root_cause_report.md`
- `diagnostics/rope_visual_vs_physical_report.md`
- `diagnostics/controller_semantics_relevance_report.md`
- `diagnostics/why_robot_spheres_need_inflation_ranked_report.md`

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [robot_visible_rigid_tool_baseline.md](./robot_visible_rigid_tool_baseline.md)
- [robot_rope_franka_physical_blocking.md](./robot_rope_franka_physical_blocking.md)

## Current Conclusion

The ranked diagnosis now points to:

- primary: wrong contact reference geometry plus XY laydown/path miss
- secondary: the rope became physically thinner than the old mental model, with
  stale Z assumptions and proxy semantics adding confusion

The evidence-backed recommendation is:

- do not treat sphere inflation as a physical need
- keep sphere inflation at most as a temporary diagnostic aid
- treat `ee_contact_radius` as `diagnostic only`, not as a real robot contactor
  size parameter
- do not use `ee_contact_radius`-driven proxy surfaces as contact proof
- do not allow `ee_contact_radius`-driven proxy surfaces as a final acceptance
  surface
- use direct-finger re-certification only after reference geometry and
  laydown/path alignment are corrected
- treat the promoted visible-tool baseline as the current conservative honest
  control for meeting-facing contact claims
