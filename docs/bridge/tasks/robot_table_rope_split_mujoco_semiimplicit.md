> status: active
> canonical_replacement: none
> owner_surface: `robot_table_rope_split_mujoco_semiimplicit`
> last_reviewed: `2026-04-13`
> review_interval: `14d`
> update_rule: `Update when the milestone boundary, coupling mode, artifact contract, or recommended implementation path changes.`
> notes: Active task for a split robot/table/rope demo that uses MuJoCo on the native robot/table side and SemiImplicit on the bridged rope side, with direct-finger contact and physical rope rendering.

# Task: Robot Table Rope Split MuJoCo SemiImplicit

## Question

How should the repo implement a truthful direct-finger Panda + native rigid
table + PhysTwin rope demo when:

- robot/table are driven by a native rigid-body path
- rope remains a SemiImplicit deformable object
- rope must visibly rest on the table/ground and render at its real physical
  thickness
- the implementation must follow official Newton example patterns rather than
  retired local robot demo practices?

## Why It Matters

This is the current best path to a meeting-facing direct-finger rope demo
without reviving the old monolithic bridge robot stack:

- `robot_panda_hydro` already demonstrates the right rigid manipulation shape
- the new native robot/table probe already shows that MuJoCo robot + native
  table blocking is stable in this repo
- the remaining work is honest split coupling to the SemiImplicit rope path

## Current Status

- Active
- Opened on `2026-04-13`
- Initial implementation target is `one_way`; `two_way` is explicitly the next
  milestone, not a hidden assumption for first acceptance
- Code and wrapper now exist
- Rope default total object mass is now `0.1kg` through the shared bridge
  `weight_scale` path
- Rope default physical radius is now `0.2x` of the previous value through the
  shared bridge `particle_radius_scale` path
- Recording now starts from post-settle state by default
- The demo now tracks support penetration proxies and no longer treats
  support-contact counts alone as success
- Best-known one-way fine-step artifact:
  - keeps `rope_table_contact` and `rope_ground_contact` true in the same run
  - keeps `rope_render_matches_physics = true`
  - keeps `robot_table_contact_frames = 0`
  - still misses `finger first contact`

## Code Entry Points

- Native rigid-side probe:
  - `Newton/phystwin_bridge/demos/demo_native_robot_table_penetration_probe.py`
- New split demo:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
- New wrapper:
  - `scripts/run_robot_table_rope_split_demo.sh`
- Relevant bridge helpers:
  - `Newton/phystwin_bridge/demos/bridge_deformable_common.py`
  - `Newton/phystwin_bridge/demos/bridge_shared.py`
  - `Newton/phystwin_bridge/demos/rope_demo_common.py`
  - `Newton/phystwin_bridge/tools/core/newton_import_ir.py`
- Official references:
  - `Newton/newton/newton/examples/robot/example_robot_panda_hydro.py`
  - `Newton/newton/newton/examples/ik/example_ik_franka.py`
  - `Newton/newton/newton/examples/cloth/example_cloth_hanging.py`
  - `Newton/newton/newton/examples/diffsim/example_diffsim_cloth.py`
  - `Newton/newton/newton/examples/mpm/example_mpm_twoway_coupling.py`

## Workflow Surfaces

- Contract:
  - [../../../tasks/contracts/robot_table_rope_split_mujoco_semiimplicit.md](../../../tasks/contracts/robot_table_rope_split_mujoco_semiimplicit.md)
- Handoff:
  - [../../../tasks/handoffs/robot_table_rope_split_mujoco_semiimplicit.md](../../../tasks/handoffs/robot_table_rope_split_mujoco_semiimplicit.md)

## Canonical Commands

```bash
bash scripts/run_robot_table_rope_split_demo.sh
python scripts/validate_experiment_artifacts.py <out_dir> --require-video --require-gif --summary-field rope_motion_after_contact --summary-field rope_render_matches_physics
python scripts/lint_harness_consistency.py
```

Mass-control flags now supported by the split demo:

- `--auto-set-weight` (default `0.1`)
- `--mass-spring-scale`
- `--object-mass`
- `--particle-radius-scale` (default `0.2`)

## Required Artifacts

- experiment directory with:
  - `README.md`
  - `command.sh`
  - `run.log`
  - `summary.json`
  - `scene.npz`
  - `timeseries.csv`
  - `hero.mp4`
  - `hero.gif`
  - `contact_sheet.jpg`
- optional stage-1/two-way additions:
  - `reaction_timeseries.csv`
  - `two_way_ablation.json`

## Success Criteria

- one-way split demo runs end-to-end from a wrapper
- rope settles into a table-edge drape and visibly contacts both table and ground
- finger first contact is detectable before rope motion
- rope render radius equals the physical radius used by the solver
- task status records the artifact path and current milestone conclusion

## Latest Artifact

- Best-known one-way run:
  - `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
  - `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`
- Default-mass validation run:
  - `/tmp/robot_table_rope_split_weight_0p1_default/summary.json`
  - `/tmp/robot_table_rope_split_weight_0p1_default/hero.mp4`
  - `/tmp/robot_table_rope_split_weight_0p1_default/contact_sheet.jpg`
- Default-radius validation run:
  - `/tmp/robot_table_rope_split_radius_0p2_default/summary.json`
  - `/tmp/robot_table_rope_split_radius_0p2_default/hero.mp4`
  - `/tmp/robot_table_rope_split_radius_0p2_default/contact_sheet.jpg`
- Calibrated light-rope run:
  - `/tmp/robot_table_rope_split_candidate_c/summary.json`
  - `/tmp/robot_table_rope_split_candidate_c/hero.mp4`
  - `/tmp/robot_table_rope_split_candidate_c/first_30_frames_sheet.jpg`
- Penetration-gate default run:
  - `/tmp/robot_table_rope_split_penetration_gate_default/summary.json`
  - `/tmp/robot_table_rope_split_penetration_gate_default/hero.mp4`
  - `/tmp/robot_table_rope_split_penetration_gate_default/first_30_frames_sheet.jpg`
- Current conclusion:
  - the split solver architecture is viable at the fine rope timestep
  - the light-rope setup no longer needs to pass only a fly-away check; it must
    also pass a non-burying support gate
  - `candidate_c` is no longer treated as a passing default, because it keeps
    contact by burying into the support geometry
  - the remaining blocker is still support calibration under the new
    non-burying gate; finger-targeting comes after that

## Open Questions

- Does the first direct-finger layout already yield a clean single-leading-pad
  contact window, or does that require a follow-up orientation tweak?
- Is the SemiImplicit body-force output sufficiently clean for the planned
  two-way wrench feedback, or will that stage need additional filtering?

## Related Pages

- [../../newton/robot_example_patterns.md](../../newton/robot_example_patterns.md)
- [native_robot_table_penetration_probe.md](./native_robot_table_penetration_probe.md)
- [../../decisions/2026-04-09_robot_ps_interaction_retirement.md](../../decisions/2026-04-09_robot_ps_interaction_retirement.md)
