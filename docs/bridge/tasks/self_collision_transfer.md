# Task: Self-Collision Transfer Decision

## Primary Question

This is now a **decision task**, not an open-ended “keep experimenting” task.

The final question is:

**Without breaking the current Newton bridge mainline, which self-collision path is the smallest, most stable, and most sufficient to support meeting-quality demos?**

This task must end with one explicit decision:

- **A. Native Newton is enough**
- **B. Bridge-side custom filtered penalty is enough**
- **C. Bridge-side PhysTwin-style self-collision is necessary**

It is **not** acceptable to finish this task with only “more experiments are needed”.

## Non-Goals

This task is **not** trying to:

- fully replicate PhysTwin self-collision behavior inside Newton
- prove Newton native self-collision is universally correct
- rewrite the entire collision stack for one bunny/thin-geometry failure
- keep doing broad black-box parameter sweeps
- silently mix Newton-only rigid/shape contacts into a mode called `phystwin`

## Why This Matters

The advisor has already clarified two constraints:

- exact collision parity is not the main project goal
- but we still need to understand the mechanism before deciding whether to override anything

So the real deliverable is a **defendable engineering decision**:

- do nothing
- keep only pair filtering
- or add a minimal bridge-side PhysTwin-style collision path

## Existing Experimental Base

The repo already contains the right scaffolding for a decision:

- `Newton/phystwin_bridge/demos/demo_cloth_box_drop_with_self_contact.py`
  - box-support decision demo for `off/native/custom`
  - `phystwin` is intentionally unsupported there because strict PhysTwin contact
    semantics do not define generic box-support contact
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`
  - graph-hop exclusion
  - filtered bridge-side penalty pairs
  - bridge-side PhysTwin-style velocity correction
  - PhysTwin-order force update and implicit ground-plane integration
- `Newton/phystwin_bridge/tools/core/phystwin_contact_stack.py`
  - shared strict bridge-side `phystwin` contact stack
  - reusable validation, context construction, and substep hook for the
    PhysTwin-native cloth case
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
  - force-diagnostic path for external rigid-contact sanity checks
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
  - profiling breakdown infrastructure for `internal_force`, `collision_contact`, and `integration`
- `Newton/phystwin_bridge/tools/core/validate_parity.py`
  - OFF-baseline regression thresholds and parity checks

That means the next step is not “add more framework”, but “turn the current framework into decision evidence”.

## Controlled Decision Matrix

## Fixed Conditions

For the main decision matrix, keep the following fixed:

- same PhysTwin strict IR
- same `mass-spring-scale`
- same `sim_dt`
- same `substeps`
- same `drop-height`
- same `contact-dist-scale`
- fixed box support
- fixed camera/viewer settings

Do **not** use bunny for the main self-collision decision. Bunny mixes in thin-geometry rigid-contact effects.

## Main Modes To Compare

Run the box self-contact task under:

- `--self-contact-mode off`
- `--self-contact-mode native`
- `--self-contact-mode custom --custom-self-contact-hops 1`
- `--self-contact-mode custom --custom-self-contact-hops 2`

This is the core cloth+box decision matrix. Strict `phystwin` parity is tracked
separately on the PhysTwin-native cloth case because the PhysTwin source only
defines:

- pairwise `object_collision`
- implicit `z=0` `integrate_ground_collision`

It does **not** define generic box / rigid-shape contact for this spring-mass
path.

## Follow-Up Sanity Check

After selecting the leading candidate from the box matrix:

- run a bunny external-contact sanity check
- keep the selected self-contact mode fixed
- use the existing `--force-diagnostic` path to confirm the selected self-contact mode does not destabilize the rigid-contact analysis

This is a **sanity check**, not the primary decision experiment.

## Regression Check

After the preferred mode is chosen:

- rerun the existing OFF-baseline parity validator
- confirm that bridge-side self-collision work did not silently damage the OFF baseline path

The self-collision task must not be allowed to break the current no-self-contact mainline.

## Required Metrics

## Metrics Already Available

The current box self-contact script already exposes useful summary fields:

- `all_particle_positions_finite`
- `final_nonexcluded_self_contact_pair_count`
- `final_nonexcluded_self_contact_max_overlap_m`
- `final_nonexcluded_self_contact_p95_overlap_m`
- `max_penetration_depth_box_m`
- `final_penetration_p99_box_m`
- `wall_time_sec`
- `self_contact_mode`
- `custom_self_contact_hops`
- `excluded_pair_count`

These are necessary, but not sufficient.

## Metrics That Must Be Added

The current overlap statistics are still too weak because they focus on the **final frame**.
That can miss transient explosions that settle down later.

Before this task can be closed, add:

- `particle_radius_median_m`
- `particle_radius_p95_m`
- `peak_nonexcluded_self_contact_pair_count_over_time`
- `peak_nonexcluded_self_contact_max_overlap_m_over_time`
- `peak_nonexcluded_self_contact_p95_overlap_m_over_time`
- `max_particle_speed_mps`
- `max_spring_stretch_ratio`
- `profile_collision_contact_share`
- `profile_internal_force_share`

The peak-over-time overlap metrics are the most important gap to close first.

## Acceptance Thresholds

## Minimum “Meeting-Ready” Pass Line

The selected mode must satisfy all of these:

1. `all_particle_positions_finite == true`
2. no visible self-explosion / cloth clumping / obvious numerical collapse
3. `peak_nonexcluded_self_contact_p95_overlap_m_over_time <= 0.5 * particle_radius_median_m`
4. `peak_nonexcluded_self_contact_max_overlap_m_over_time <= 1.0 * particle_radius_median_m`
5. `final_penetration_p99_box_m <= 0.5 * particle_radius_median_m`
6. `max_penetration_depth_box_m <= 1.0 * particle_radius_median_m`
7. `wall_time_sec(selected_mode) / wall_time_sec(off) <= 2.0`
8. produce one clean 8–15 second MP4 that is usable in slides

## Stronger “Promote To Mainline” Pass Line

If the selected mode is going to become the preferred longer-term path, it should also satisfy:

9. bunny sanity-check does not clearly worsen rigid-contact behavior
10. OFF baseline parity still passes the existing validator thresholds

## Decision Logic

The task must end with this logic:

- **If native passes**: stop there; do **not** copy PhysTwin
- **If native fails but custom passes**: conclusion is “pair filtering is enough”
- **Only if native fails, custom fails, and phystwin passes**: allow “bridge-side PhysTwin-style self-collision is needed”

This rule prevents overfitting the project onto the most invasive option.

## Risks To Track

- final-frame overlap statistics can hide transient failure
- graph-hop exclusion is not the same as true geometric-neighbor exclusion
- if `phystwin` wins, that is a bridge-side result, not a Newton-native claim
- strict `phystwin` parity currently applies only to the PhysTwin-native cloth
  contact set (self-collision + implicit ground plane)
- bunny should not be the primary decision scene because it mixes self-contact with thin rigid geometry
- inflating particle radius is not a valid replacement for a self-collision decision

## Required Outputs

The task is not complete until it produces all of the following:

1. `self_collision_decision_table.csv`
2. `self_collision_decision.md`
3. one 4-panel comparison figure across modes
4. one clean MP4 for the selected mode
5. one slide-ready summary page with the final recommendation

## Success Criteria

This task is complete only when:

- the box decision matrix has been run
- peak-over-time overlap metrics have been added
- a bunny rigid-contact sanity check has been performed on the selected mode
- parity regression has been rechecked for the OFF baseline
- profiling has been attached to the selected mode
- the result can be stated as one of A / B / C above

## Current Recommendation For Execution Order

1. run the box decision matrix
2. add peak-over-time overlap metrics
3. run the bunny force-diagnostic sanity check
4. run profiler on the selected candidate
5. write the decision table and slide-ready conclusion
