# Current Status

Last updated: 2026-04-01

This page is the shortest operational summary of the bridge project.
It should stay current and be updated whenever a task changes state.

## Confirmed

- PhysTwin -> Newton bridge baseline exists for the main recall demos.
- Deformable-rigid interaction is demonstrated for rope + bunny.
- A native Newton robot-asset baseline now exists for robot + deformable:
  - `demo_robot_rope_franka.py`
  - native Franka Panda URDF
  - bridge rope
  - `mp4 + gif + summary.json` artifacts
- A separate stage-0 sanity-baseline scaffold now exists for the native robot
  rope release/drop case:
  - `docs/bridge/tasks/native_robot_rope_drop_release.md`
  - `results/native_robot_rope_drop_release/`
  - narrow claim boundary: release, free fall, real ground contact, 1:1
    presentation timing
- A recoil-fixed stage-0 native-robot release/drop baseline now exists:
  - `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5`
  - `final_presentation.mp4`
  - `final_debug.mp4`
  - `summary.json`
  - `physics_validation.json`
  - `qa/contact_sheet.png`
  - `qa/event_sheet.png`
  - `qa/verdict.md`
  - matched drag comparison:
    - `results/native_robot_rope_drop_release/drag_ab_compare.json`
  - current conclusion:
    - both recoil-fixed drag OFF and drag ON runs pass settle, kick, gravity,
      ground-contact, and video-readability gates
    - drag effect on the recoil-fixed pair is minor rather than causal
    - the drag-OFF run is the promoted best because it is the simpler
      baseline while already passing the full gate set
- A meeting-ready canonical native Franka result bundle now exists:
  - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`
  - validated `final.mp4`
  - `ffprobe.json`
  - `contact_sheet.png`
  - `event_sheet.png`
  - `validation.json`
  - `verdict.md`
  - summary fields aligned with the visible finger-span interaction
  - phase-gated drag now keeps the release readable without reintroducing the
    old proxy mismatch
  - promoted bundle now also has a run-local `README.md`, a stricter
    `manifest.json`, and `SLIDE_READY.md`
- Weight scaling is not a single-mass knob; bridge-side scaling logic couples
  mass and spring/contact parameters.
- Force diagnostics for cloth vs bunny now support:
  - signed-distance-aware geometry analysis
  - geometry-contact vs force-contact masks
  - internal vs external normal-force visualization
  - parity check between diagnostic and baseline first-contact behavior
- A first 4-case bunny mechanism matrix has now been run under a fixed
  `0.1 kg cloth / 0.5 kg rigid` workpoint:
  - bunny baseline
  - box control
  - bunny low inertia
  - bunny larger scale
- Current evidence from that matrix supports:
  - not a wrong-direction failure
  - not a generic rigid-contact failure
  - a geometry- and momentum-sensitive sparse-contact failure on bunny
- A historical full-process synchronized bunny force package exists under:
  - `results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2`
  - it still supports the older 4-case mechanism claim package
  - but it is no longer the final meeting visualization target for this task
  - the bunny task is now reopened for a stricter real-time all-colliding-node
    `2 x 2` board:
    - `box penalty`
    - `box total`
    - `bunny penalty`
    - `bunny total`
- No-render realtime profiling exists for the interactive viewer and already
  separates collision, solver-path, and render interpretations.
- A canonical apples-to-apples rope performance bundle now exists:
  - `results/rope_perf_apples_to_apples/`
  - Newton A0/A1 throughput
  - Newton A2/A3 attribution
  - PhysTwin B0 headless throughput
  - PhysTwin B1 headless attribution
  - Nsight A1/B0 traces
  - updated `0401` profiling slides/transcript
- Current rope performance conclusion is now evidence-based:
  - same-case parity is established on `rope_double_hand`
  - Newton precomputed replay is still about `3.30x` slower than PhysTwin
    headless replay in `ms/substep`
  - controller bridge tax is real (`~1.87x` A0 -> A1 speedup)
  - pure rope replay is not collision-bound
  - Nsight supports a graph-launch / execution-structure explanation rather than
    a collision explanation
- Most offline video renderers now use a unified earth-tone ground palette.
- The old proxy robot demo has been retired; the Franka native-asset line is
  now the canonical robot + deformable path.
- Robot + deformable presentation framing was tightened further in
  `demo_robot_rope_franka.py`:
  - hero camera now defaults to the contact region
  - validation camera preset is recorded in `summary.json`
  - earth-tone ground grid makes the work surface easier to read
  - stage/anchor support geometry is slightly more visible in presentation mode
  - latest validation run:
    - `results/robot_deformable_demo/runs/20260331_030148_native_franka_lift_release_presentation`
- A repo-native Codex harness baseline now exists:
  - short root `AGENTS.md`
  - subtree `AGENTS.md` files for bridge / PhysTwin / docs / scripts
  - top-level `plans/` and `tasks/` scaffolding
  - committed authoritative results metadata under `results_meta/`
  - repo-local `.agents/skills/`
  - repo-local `.codex/` config + hooks
  - canonical wrapper scripts and an artifact validator
  - retired root singleton task docs removed
    - `Plan.md`
    - `Status.md`
    - `Prompt.md`
    - `DecisionLog.md`
  - duplicate orphan bunny full-process scaffold docs removed in favor of the
    canonical `bunny_penetration_force_diagnostic` task and its accepted result
    bundle
  - skeptical video acceptance surfaces now exist under:
    - `docs/evals/video_acceptance_rubric.md`
    - `docs/evals/video_evaluator_prompt.md`
    - `scripts/prepare_video_review_bundle.py`
    - `scripts/run_skeptical_video_audit.py`
  - harness drift is now checked mechanically by:
    - `scripts/lint_harness_consistency.py`

## Active Workstreams

- Harness engineering upgrade
- Bunny penetration mechanism analysis
- Bunny real-time all-colliding-node `2 x 2` meeting visualization rework
- Interactive playground profiling and interpretation
- Rope apples-to-apples performance investigation
- Self-collision research / transfer question
- Robot + deformable claim hardening around the native Franka baseline
- Native robot rope drop/release sanity baseline
- Video presentation quality
- Data collection protocol
- Fast-FoundationStereo evaluation

## Recently Strengthened

- `demo_cloth_bunny_drop_without_self_contact.py`
  - stronger force diagnostic pipeline
  - signed distance on bunny mesh
  - parity check
  - trigger-plus-N snapshot support
  - direct diagnostic MP4 output
  - process and force artifacts are now split into distinct outputs
  - full-process phenomenon clips now run long enough for meeting playback
  - force artifacts now use the stable phenomenon render as the global panel
  - projected 2D force overlays + zoom panel now replace the old trigger-only
    force montage as the canonical presentation path
  - active contact interval is now exact-frame synchronized in the final force
    videos
  - phenomenon HUD penetration metric is now labeled as mesh penetration rather
    than the older ambiguous proxy wording
- `demo_cloth_box_drop_with_self_contact.py`
  - rollout-peak self-overlap metrics
  - particle-radius reference stats
  - max particle speed and spring-stretch summary fields
- self-collision decision tooling
  - box matrix runner now exists
  - operator-level PhysTwin-style equivalence verifier now exists
  - shared strict bridge-side `phystwin` contact stack now exists:
    - `Newton/phystwin_bridge/tools/core/phystwin_contact_stack.py`
    - strict scope: pairwise self-collision + implicit `z=0` ground plane
    - no Newton core change
  - final self-collision campaign now exists under:
    - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0`
  - bridge-side PhysTwin exactness passed in that campaign:
    - `max_abs_dv = 1.1324882507324219e-06`
    - `median_rel_dv = 4.070106739010465e-08`
  - cloth+box `phystwin` is now intentionally guarded as unsupported in the demo:
    - strict `phystwin` parity is not claimed on Newton-only box-support scenes
  - QC-passing cloth-box `phystwin` hero video now exists:
    - `selected/self_collision_on_cloth_box_phystwin.mp4`
  - QC-passing parity support demo now exists:
    - `selected/parity_support_demo.mp4`
  - strict self-collision parity on the in-scope cloth reference case is currently blocked:
    - old campaign bundle: `rmse_mean = 0.025657856836915016`
    - latest shared-stack scratch run improves that to about `0.010737196542322636` on the full 302-frame case, but still misses the `1e-5` gate
    - blocker doc:
      - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/BLOCKER_strict_self_collision_parity_bridge_rollout_mismatch.md`
- `docs/`
  - initial encyclopedia skeleton
  - bridge/newton/phystwin separation
  - runbooks / evals / decisions / generated sections
- `results/rope_perf_apples_to_apples/`
  - canonical benchmark tree with stage manifests, methodology, conclusions,
    and Nsight sidecars
- `scripts/`
  - `benchmark_phystwin_rope_headless.py`
  - `run_rope_perf_apples_to_apples.sh`
  - `run_rope_perf_nsight.sh`
  - `summarize_rope_perf_apples_to_apples.py`
- repo harness
  - `TODO.md` is now a task index instead of a detail dump
  - wrapper scripts now write `command.sh` and `run.log`
  - validator exists for experiment artifact contracts
  - Codex-specific control plane files now exist in `.codex/`
  - `results/bunny_force_visualization/` now has a canonical index, pointer
    files, per-run templates, and a lightweight visual QA workflow for bunny
    force-visualization runs
- `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
  - native Franka Panda asset
  - IK-driven articulation control
  - drop/release baseline task preset with real ground contact and saved
    physics-validation sidecar
  - summary fields aligned with presentation acceptance
  - finger-span contact proxy now replaces the old gripper-center-only contact summary
  - canonical wrapper + strict video validation now land under `results/robot_deformable_demo/`
  - promoted bundle now includes a run-local `README.md`, a stricter `manifest.json`, and slide-ready bundle templates
  - the separate stage-0 release/drop bundle now has a recoil-fixed promoted
    baseline with settle and horizontal-kick diagnostics

## Still Missing

- Committed results metadata mirrors for every major authoritative run family
- A hard skeptical video evaluator layer separate from optimistic automatic QC
- One standard harness-consistency lint pass in normal task closeout
- Rope-side force diagnostic at the same level as cloth-side diagnostic
- Full self-collision decision result across the complete box matrix
- Final decision on whether strict parity can reach `1e-5` under bridge-only changes
  - current campaign evidence says the best bridge-only result is still around `1.95e-5`
- Canonical experiment templates applied consistently across existing `tmp/`
- Existing experiment directories backfilled so the artifact validator passes
- Standard run scripts adopted as the default workflow by everyone
- Filled-in encyclopedia pages beyond the initial structural level
- A stronger “robot feels deformable resistance” claim beyond the current
  native-asset interaction baseline
- A fresh trusted Codex session confirming `.codex/config.toml` + hooks behave
  as intended end-to-end inside the actual agent runtime
- More canonical wrappers beyond the first wave (`bunny diag`, `realtime profile`,
  `robot rope`, `gif render`)

## Related Pages

- [open_questions.md](./open_questions.md)
- [experiment_index.md](./experiment_index.md)
- [tasks/README.md](./tasks/README.md)
