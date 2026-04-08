# Status: robot_rope_franka_physical_blocking

## Current State

- Active
- This is a new stronger task, separate from the accepted tabletop-push
  baseline
- Current state is now: `Stage-0 direct-finger rigid-only blocking passes on
  the repaired bridge-layer joint_target_drive path; Stage-1 rope-integrated
  runs now preserve body-truth and artifact truth, but the best current
  candidates still fail visual acceptance because the arm settles into a long
  table-loaded posture / late-scene collapse rather than a clean,
  presentation-ready finger-blocking push`

## Last Completed Step

- Repaired the bridge-layer `joint_target_drive` truth path so the solver owns
  `state_out.body_q`:
  - no pre/post hard overwrite in the blocking path
  - reduced-state resync now comes from `eval_ik(...)` after `solver.step(...)`
- Added stage-aware blocking support directly in
  [demo_robot_rope_franka.py](../../Newton/phystwin_bridge/demos/demo_robot_rope_franka.py):
  - `--blocking-stage rigid_only|rope_integrated`
  - `rigid_only` removes the rope while keeping the same direct-finger
    controller truth
  - `rope_integrated` keeps the rope and reuses the same same-history render
    chain
- Added fail-closed stage truth to the canonical wrapper and rendered videos:
  - wrapper now requires `--blocking-stage`
  - top-level Stage-1 artifacts are copied as
    `rope_integrated_hero_presentation.mp4` /
    `rope_integrated_hero_debug.mp4` /
    `rope_integrated_validation_camera.mp4`
  - Stage-0/Stage-1 presentation videos now carry explicit stage watermarks
- Added hidden-preroll robot reset support for the blocking path:
  - `--tabletop-reset-robot-after-preroll`
  - used only to keep rope settle hidden from the visible clip; visible-frame
    control truth remains `joint_target_drive`
- Reworked the canonical wrapper and validators:
  - [run_robot_rope_franka_physical_blocking.sh](../../scripts/run_robot_rope_franka_physical_blocking.sh)
  - [diagnose_robot_rope_physical_blocking.py](../../scripts/diagnose_robot_rope_physical_blocking.py)
  - [validate_robot_rope_franka_physical_blocking.py](../../scripts/validate_robot_rope_franka_physical_blocking.py)
  - wrapper now produces `command.txt`, same-history hero/debug/validation,
    direct-finger diagnostics, and artifact-contract validation
- Produced the first truthful Stage-0 pass:
  - [c08_stage0_directfinger_renderfix](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_165753_rigid_only_c08_stage0_directfinger_renderfix)
  - key metrics:
    - `robot_table_first_contact_time_s = 0.1334`
    - `robot_table_penetration_min_m = -9.76e-4`
    - `ee_target_to_actual_error_during_block_mean_m = 6.98e-2`
    - `proof_surface = actual_multi_box_finger_colliders`
    - blocking validator: PASS
- Produced the first rope-integrated bridge-layer candidates on the same
  architecture:
  - [c10_stage1_prerollreset](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_170744_rope_integrated_c10_stage1_prerollreset)
  - [c11_stage1_holdtune](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171151_rope_integrated_c11_stage1_holdtune)
  - [c12_stage1_basez09](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171603_rope_integrated_c12_stage1_basez09)
  - [c13_stage1_higherhold](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_171950_rope_integrated_c13_stage1_higherhold)
- Added a blocking-specific joint-space reference family:
  - `--tabletop-joint-reference-family blocking_lowprofile`
  - shallower push start / push end waypoints recovered from the best
    solver-realized Stage-1 postures instead of reusing the old accepted
    readable-baseline family verbatim
- Added Stage-1-specific non-finger loading diagnostics and gates:
  - `first_nonfinger_table_contact_time_s`
  - `nonfinger_table_contact_duration_s`
  - `nonfinger_penetration_min_m`
  - `collapse_after_retract_detected`
  - `collapse_frame_idx`
  - `fr3_link7/fr3_link6/fr3_link5` minima when present
- Produced three new rope-integrated candidates on the new family:
  - [c14_lowprofile_base06](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_194528_rope_integrated_c14_lowprofile_base06)
  - [c15_lowprofile_shortretract](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_194810_rope_integrated_c15_lowprofile_shortretract)
  - [c16_lowprofile_hi_clearance](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_194847_rope_integrated_c16_lowprofile_hi_clearance)
- Audited the Stage-1 rear support/backstop box and upgraded it from a
  render-only prop to a real native Newton static box collider:
  - new tabletop arg: `--tabletop-support-box-mode`
  - current blocking wrapper now uses `--tabletop-support-box-mode physical`
  - same box dimensions/transform now drive both render and physics
- Added support-box-aware diagnostics and validator surfaces:
  - `support_box_contact_report.json`
  - `support_box_penetration_plot.png`
  - `support_box_contact_duration_s`
  - `support_box_penetration_min_m`
  - `support_box_contact_link_names`
  - `support_box_peak_penetrating_link_name`
  - `support_box_contact_fraction_after_first_touch`
  - validator `--require-support-box`
- Produced three new support-box-aware Stage-1 candidates:
  - [c17_supportbox_shortretract](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_210340_rope_integrated_c17_supportbox_shortretract)
  - [c18_supportbox_base06](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_210403_rope_integrated_c18_supportbox_base06)
  - [c19_supportbox_hi_clearance](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260407_210403_rope_integrated_c19_supportbox_hi_clearance)
- Replaced the old inherited support-box default in
  [demo_robot_rope_franka.py](../../Newton/phystwin_bridge/demos/demo_robot_rope_franka.py)
  with a blocking-task-specific thin backstop slab for
  `joint_target_drive` Stage-1 runs:
  - default support box no longer reuses `robot_base_scale/center` verbatim
  - metadata now records:
    - `support_box_default_center`
    - `support_box_default_scale`
    - `support_box_geometry_source`
    - `support_box_normal_axis`
    - `support_box_normal_sign`
- Extended support-box diagnostics and validator surfaces:
  - `support_box_fit_report.json`
  - `support_box_fit_report.md`
  - `frame0_support_box_overlap_detected`
  - `first_support_box_contact_phase`
  - `robot_support_box_first_contact_time_s`
  - validator gates for:
    - frame-0 overlap absent
    - first support contact in `approach/push`
    - first support contact after settle
    - support contact links restricted to `fr3_link5/6/7/hand`
- Extended the canonical wrapper with scout-fit support-box workflow:
  - wrapper now accepts:
    - `--support-box-fit-report`
    - `--support-box-fit-profile A|B|C`
  - selected geometry is written to `selected_support_box_geometry.json`
  - summary/README now record the chosen support-box geometry surface
- Produced the clean-start no-box scout run:
  - [support_scout_no_box](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_043258_rope_integrated_support_scout_no_box)
  - its `support_box_fit_report.json` now drives the first A/B/C slab family
- Produced the rebuilt no-box scout with actual-collision candidate eval:
  - [support_scout_no_box_v2b](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_060437_rope_integrated_support_scout_no_box_v2b)
  - `support_box_fit_report.json` now includes per-candidate `actual_eval` from
    rebuilt Newton models rather than only center-gap heuristics
- Produced the first thin-slab A/B/C Stage-1 runs and one bounded
  support-normal refinement:
  - [support_box_A](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_043554_rope_integrated_support_box_A)
  - [support_box_B](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_043832_rope_integrated_support_box_B)
  - [support_box_C](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_044121_rope_integrated_support_box_C)
  - [support_box_B_refine_front06](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_044557_rope_integrated_support_box_B_refine_front06)
- Produced the first Stage-1 candidates with real later support contact on a
  physical support box:
  - [support_box_shortsettle_probe](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_062738_rope_integrated_support_box_shortsettle_probe)
  - [support_box_shortsettle_midtrim](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_063326_rope_integrated_support_box_shortsettle_midtrim)

## Latest Findings

- The current promoted tabletop hero remains a readable baseline only
- The old overwrite path is definitively non-physical and remains out of scope
  for the stronger claim.
- The repaired bridge-layer path is now strong enough to prove Stage-0 direct
  finger blocking without touching `Newton/newton/`.
- Stage-0 direct-finger proof surface is now explicit and stable:
  - actual imported finger-box colliders against the native table box
  - `ee_contact_radius` stays diagnostic-only and is not part of final proof
- The rope-integrated path now has working body-truth / artifact-truth
  infrastructure:
  - same-history hero/debug/validation
  - stage-aware blocking validator
  - artifact validator passes
  - `blocking_stage` is now written into the normal `summary.json`
- Artifact truth is now fail-closed for this task:
  - wrapper refuses to run without explicit `--blocking-stage`
  - rigid-only presentation outputs are labeled `RIGID ONLY — NO ROPE BY DESIGN`
  - rope-integrated presentation/debug/validation outputs are labeled
    `ROPE INTEGRATED`
  - Stage-0 and Stage-1 top-level video filenames now encode the stage
- Stage-1 can now be evaluated against the actual failure mode rather than only
  finger-vs-table blocking:
  - `c14/c15/c16` all pass the new non-finger loading gates
  - for all three, `nonfinger_table_contact_duration_s = 0.0`
  - for all three, `collapse_after_retract_detected = false`
  - all three keep `proof_surface = actual_multi_box_finger_colliders`
- New family comparison:
  - `c14`:
    - passes new Stage-1 gates
    - `robot_table_penetration_min_m = -0.001927`
    - `rope_com_displacement_m = 0.02240`
    - visually the cleanest first proof that finger-only blocking can coexist
      with visible rope
  - `c15`:
    - passes new Stage-1 gates
    - `robot_table_penetration_min_m = -0.001877`
    - `rope_com_displacement_m = 0.03266`
    - best current local presentation candidate because rope motion is more
      visible than `c14` while still avoiding any measured non-finger table
      loading or late collapse
  - `c16`:
    - passes new Stage-1 gates
    - `robot_table_penetration_min_m = -0.001912`
    - `rope_com_displacement_m = 0.03127`
    - higher contact/push clearance delays early loading a bit, but the visible
      story is not stronger than `c15`
- Current best truthful interpretation:
  - Stage-0 is solved at the bridge layer
  - Stage-1 is no longer blocked by controller truth
  - the old accepted readable-tabletop joint family was the main Stage-1 visual
    blocker
  - the new `blocking_lowprofile` family plus non-finger gating produces the
    first local rope-integrated candidates that are numerically and visually
    aligned enough to review as presentation-ready candidates
  - no promoted authority has been created yet; the strongest local candidate
    is currently `c15`
- Support-box truth audit result:
  - before this step, the visible rear box was only the rendered
    `/demo/robot_pedestal`; it was not present in `model.shape_count`
  - after the bridge-layer patch, the box is now a real world shape:
    - `support_box_is_physical_collider = true`
    - shape label/index: `tabletop_support_box / 55`
- What the new support-box runs proved:
  - `c17/c18/c19` all show real support-box contact on
    `fr3_link5` and `fr3_link6`
  - the box is therefore no longer “just visible story”; it is in the actual
    physics path
- What they also revealed:
  - the current support-box geometry is too aggressive
  - all three support-box candidates begin support contact at frame `0`
  - all three fail the new support-box penetration gate with deep overlap:
    - `c17`: `support_box_penetration_min_m = -0.22690`
    - `c18`: `support_box_penetration_min_m = -0.22689`
    - `c19`: `support_box_penetration_min_m = -0.22690`
  - although finger blocking, rope visibility, and non-finger table loading all
    remain acceptable, the box is currently acting as an overlapping pillar
    rather than a clean backstop
- Current best truthful interpretation at this new boundary:
  - support box is now a real proof surface candidate
  - but the present support-box geometry is still too intrusive to support a
    stronger-task promotion
  - the next honest move is support-box geometry retuning, not more truth-path
    work or Newton core changes
- New thin-backstop result after the slab refit:
  - the box is no longer a giant pedestal by default on `joint_target_drive`
    Stage-1 runs
  - the clean-start scout run now records a physical-support fitting surface at
    [support_box_fit_report.json](../../Newton/phystwin_bridge/results/robot_rope_franka_physical_blocking/candidates/20260408_043258_rope_integrated_support_scout_no_box/support_box_fit_report.json)
  - the first A/B/C slab family eliminates the old frame-0 overlap entirely:
    - for `support_box_A/B/C`:
      - `frame0_support_box_overlap_detected = false`
      - `support_box_is_physical_collider = true`
  - but all three thin-slab runs still miss the robot completely:
    - `support_box_contact_duration_s = 0.0`
    - `support_box_contact_link_names = []`
    - no candidate reaches the new `approach/push` support-contact gate
  - bounded support-normal refinement `support_box_B_refine_front06` also
    remains a miss:
    - `frame0_support_box_overlap_detected = false`
    - `support_box_contact_duration_s = 0.0`
    - `support_box_contact_link_names = []`
  - current strongest interpretation:
    - support box truth is now fixed in both directions:
      - old large geometry: real contact but dishonest initial overlap
      - new thin slab: no overlap, but also no real support contact
    - the remaining blocker is therefore not “is the box physical?” and not
      “is the box too large?” alone; it is that the current fitted slab still
      does not intersect the actual non-finger support sweep of the robot links
      under this Stage-1 trajectory
    - the next honest move is to fit support geometry from the actual
      support-capable link geometry / contact sweep rather than from body-center
      trajectories alone
- New support-box milestone after the rebuilt actual-collision search:
  - `support_scout_no_box_v2b` confirmed that the first x-only slab family was
    still too far away even when evaluated through rebuilt Newton models
  - a bounded actual-collision search around the real support-capable geometry
    produced the first Stage-1 candidate with honest later support contact:
    - `support_box_shortsettle_probe`
    - metrics:
      - `frame0_support_box_overlap_detected = false`
      - `first_support_box_contact_phase = push`
      - `robot_support_box_first_contact_time_s = 3.30165`
      - `support_box_contact_duration_s = 1.4674`
      - `support_box_contact_link_names = ['fr3/fr3_link5']`
      - `nonfinger_table_contact_duration_s = 0.0`
      - `collapse_after_retract_detected = false`
  - this is the first run where the box is not merely physical and not merely
    non-overlapping, but is actually used as a later backstop in the real
    Stage-1 rollout
  - however it still fails the stricter support-box duration gate:
    - current max allowed: `0.50 s`
    - current measured: `1.4674 s`
  - bounded trimming confirms the current tradeoff:
    - shrinking to `0.12 / 0.06 / 0.10` removes support contact entirely
    - midpoint `0.13 / 0.07 / 0.10` keeps support, but contact starts earlier
      (`approach`) and still lasts too long (`1.1339 s`)
  - current strongest truthful interpretation:
    - support-box geometry alone is no longer the only blocker
    - we now have proof that later support is possible on the repaired
      controller truth path
    - the remaining blocker is shaping that support into a shorter, cleaner,
      presentation-ready backstop event rather than a long support interval

## Next Step

- Keep the repaired `joint_target_drive` bridge path; do not revert to state
  overwrite and do not touch `Newton/newton/`.
- Keep the thin-slab default and the support-box-aware validator gates.
- Next bounded move:
  - keep the real later-support geometry from `support_box_shortsettle_probe`
    as the new local starting point
  - retune the Stage-1 reference timing / support-box duration together so the
    support interval stays later and shorter:
    - target `support_box_contact_duration_s <= 0.50`
    - keep `frame0_support_box_overlap_detected = false`
    - keep `first_support_box_contact_phase in {approach, push}`
    - keep `nonfinger_table_contact_duration_s = 0.0`
    - keep `collapse_after_retract_detected = false`
- Preserve the stronger-task docs truthful and keep the old readable tabletop
  baseline as the only accepted robot-rope authority until a rope-integrated
  candidate is visually honest as well as numerically passing.

## Authority Rule

- Do not modify `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`
  from this task
- Only add `results_meta/tasks/robot_rope_franka_physical_blocking.json` after
  a real stronger-task pass
