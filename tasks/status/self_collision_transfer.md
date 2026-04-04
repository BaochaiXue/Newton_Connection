# Status: self_collision_transfer

## Current State

Tracked as an active task with a canonical slug and a backfilled authoritative
chain.

Committed current-bundle meaning lives in:

- `results_meta/tasks/self_collision_transfer.json`

That committed surface is still the source of truth for the current blocked
bundle. The scratch validation notes below are local exploratory evidence only
unless a new run is promoted into `results_meta/`.

The bridge now has a shared strict `phystwin` contact-stack implementation for
the PhysTwin-native cloth parity scene:

- pairwise self-collision uses the bridge-side PhysTwin operator
- ground contact uses a bridge-side implicit `z=0` PhysTwin-style integrator
- strict `phystwin` now defaults to a frame-frozen explicit collision table
  with object-only candidate semantics
- `off/native/custom` stay on their existing compatibility paths
- cloth+box `phystwin` is intentionally guarded as unsupported
- a canonical controlled `2 x 2` cloth+implicit-ground RMSE runner now exists:
  - `Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_rmse_matrix.py`
  - it exposes the two intended law axes independently:
    - `self_collision_law = off | phystwin`
    - `ground_contact_law = native | phystwin`

Local scratch validation notes:

- operator exactness still passes:
  - `max_abs_dv = 1.1324882507324219e-06`
  - `median_rel_dv = 4.070106739010465e-08`
  - `Newton/phystwin_bridge/results/tmp_verify_phystwin_equivalence_postsync_rerun.json`
- strict cloth parity 60-frame default frozen-table run:
  - `rmse_mean = 0.001314889290370047`
  - `first30_rmse = 0.00038029628922231495`
  - `last30_rmse = 0.0022494823206216097`
  - `Newton/phystwin_bridge/results/tmp_strict_phystwin_default60_postsync/strict_phystwin_default60_rollout_report.json`
- strict cloth parity 60-frame dynamic-query debug run:
  - `rmse_mean = 0.001589029561728239`
  - `first30_rmse = 0.0004093373427167535`
  - `last30_rmse = 0.002768721431493759`
  - `Newton/phystwin_bridge/results/tmp_strict_phystwin_dynamic60_postsync/strict_phystwin_dynamic60_rollout_report.json`
- table-ordering diagnostic:
  - frozen beats dynamic on `rmse_mean`, `first30_rmse`, and `last30_rmse`
  - no 500-cap truncation observed in the audited 60-frame comparison
  - `Newton/phystwin_bridge/results/tmp_collision_table_diag_v1/collision_table_diagnostic.json`
- strict cloth parity full 302-frame default frozen-table run:
  - `rmse_mean = 0.010103434324264526`
  - `last30_rmse = 0.014149246737360954`
  - `Newton/phystwin_bridge/results/tmp_strict_phystwin_default302_postsync/strict_phystwin_default302_rollout_report.json`
- matched OFF vs strict `phystwin` 302-frame comparison on the same cloth+ground case:
  - OFF `rmse_mean = 0.009786468930542469`
  - strict `phystwin` `rmse_mean = 0.010103434324264526`
  - strict `phystwin` is better only on `first30_rmse` (`0.0005582491285167634` vs `0.0023693302646279335`)
  - OFF is still better on full-rollout `rmse_mean`, `rmse_max`, and `last30_rmse`
  - `Newton/phystwin_bridge/results/tmp_off_vs_phystwin_302_compare_20260401/compare_summary.json`
- latest parity support comparison video now exists for the updated slide deck:
  - `Newton/phystwin_bridge/results/tmp_off_vs_phystwin_302_compare_20260401/parity_support_demo/parity_support_demo.mp4`
  - deck GIF: `formal_slide/meeting_2026_04_01/gif/self_collision_parity_support.gif`
- professor-facing detailed report now exists under:
  - `tmp/report/self_collision_professor_report_20260401/report.md`
  - `tmp/report/self_collision_professor_report_20260401/report.pdf`
- updated April 1 deck now includes a dedicated source-proof slide for the
  remaining self-collision gap:
  - PhysTwin `update_collision_graph()` / `update_potential_collision`
  - bridge `prepare_strict_phystwin_contact_frame()`
  - rebuilt deck: `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
- updated April 1 deck now also restructures the self-collision section into a
  four-step logic:
  - what strict `phystwin` now means
  - what is already matched
  - where the remaining mismatch likely is
  - what we are not claiming
- updated April 1 deck now removes cloth+box `phystwin` from the strict parity
  section itself and keeps that section on the in-scope cloth reference path
- controller-spring diagnostic currently reports substantial mismatch:
  - one-step `force_abs_max = 0.006733048971410349`
  - short-rollout `force_abs_max = 389.3789927564146`
  - `pass = false`
  - `Newton/phystwin_bridge/results/tmp_controller_spring_diag_v2/controller_spring_diagnostic.json`
- controlled `2 x 2` full 302-frame cloth+ground RMSE matrix now exists:
  - root:
    - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a`
  - fairness check: `pass = true`
  - exact case labels:
    - `case_1_self_off_ground_native`
    - `case_2_self_off_ground_phystwin`
    - `case_3_self_phystwin_ground_native`
    - `case_4_self_phystwin_ground_phystwin`
  - `rmse_mean` results:
    - case 1: `0.00976876262575388`
    - case 2: `0.009609504602849483`
    - case 3: `0.008761118166148663`
    - case 4: `0.009012339636683464`
  - best case by `rmse_mean` is now:
    - `case_3_self_phystwin_ground_native`
  - current main-effect reading from the fair matrix:
    - with ground fixed to native, turning on PhysTwin-style self-collision improves `rmse_mean` by about `1.01e-3`
    - with self fixed to off, switching ground native -> PhysTwin-style improves `rmse_mean` by only about `1.59e-4`
    - the current interaction effect on `rmse_mean` is positive (`~4.10e-4`), so combining both PhysTwin-style laws is not the best full-rollout pair on this scene
  - matrix summary:
    - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/rmse_matrix_summary.json`
  - fairness check:
    - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/fairness_check.md`
- OFF regression remains acceptable:
  - `rmse_mean = 0.00476811733096838`
  - `Newton/phystwin_bridge/results/tmp_off_ground_regression_60_postsync/off_ground_regression60_rollout_report.json`
- rope OFF importer smoke still passes:
  - `rmse_mean = 1.4174155694490764e-05`
  - `Newton/phystwin_bridge/results/tmp_rope_off_smoke_30_postsync/rope_off_smoke30_rollout_report.json`

## Last Completed Step

Added the canonical controlled `2 x 2` cloth+ground RMSE runner and ran the
full 302-frame matrix on the strict cloth reference scene:

- `tools/other/run_ground_contact_self_collision_rmse_matrix.py`
- bridge-side independent law exposure through:
  - `tools/core/newton_import_ir.py`
  - `tools/core/phystwin_contact_stack.py`
  - `tools/core/validate_parity.py`

The older frozen-table / controller diagnostics remain relevant supporting
evidence:

- `tools/core/phystwin_contact_stack.py`
- shared importer path via `tools/core/newton_import_ir.py`
- thin `tools/other/newton_import_ir_phystwin.py` wrapper
- `tools/other/diagnose_phystwin_collision_table.py`
- `tools/other/diagnose_controller_spring_semantics.py`
- cloth+box demo guard for unsupported `phystwin`

## Next Step

Use the new fair `2 x 2` matrix plus the existing diagnostics to determine why
`case_3_self_phystwin_ground_native` currently beats the fully PhysTwin-style
pair on full rollout:

- validate the controller-spring harness against a narrower one-step reference if needed
- decide whether the current positive interaction term is mainly due to:
  - controller-spring semantics
  - force/ground timing interaction
  - or remaining collision-table runtime differences
- rerun the fair `2 x 2` matrix after the next bridge-side change
- update `results_meta/tasks/self_collision_transfer.json` only if a new
  committed current bundle is actually promoted

## Blocking Issues

- the fair `2 x 2` matrix still misses the strict `1e-5` gate in all four cases
- under the current full 302-frame cloth+ground comparison, the best case is
  `self=phystwin, ground=native`, not the fully PhysTwin-style pair
- strict `phystwin` scope is intentionally narrow and does not yet cover box or
  other Newton-only rigid-support contacts

## Artifact Paths

- `results_meta/tasks/self_collision_transfer.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/README.md`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/fairness_check.md`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/rmse_matrix.csv`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a/rmse_matrix_summary.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/matrix/self_collision_decision.md`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/parity/strict_self_collision_parity_summary.json`
- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/video_qc/final_video_qc_report.md`
- local scratch validation notes under `Newton/phystwin_bridge/results/tmp_*`
  are secondary/local-only unless promoted into `results_meta/`
