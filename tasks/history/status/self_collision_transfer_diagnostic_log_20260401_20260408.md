> status: historical
> canonical_replacement: `../../../tasks/status/self_collision_transfer.md`
> owner_surface: `self_collision_transfer`
> last_reviewed: `2026-04-11`
> review_interval: `90d`
> update_rule: `Historical scratch log only. Do not record new active state here.`
> notes: Archived detailed diagnostic notes moved out of the active self-collision status page so the live status can stay short and operational.

# Historical Status Log: self_collision_transfer diagnostics 2026-04-01 to 2026-04-08

This file preserves the detailed local diagnostic notes that previously lived in
the active status surface. The canonical current state for the active task now
lives in `tasks/status/self_collision_transfer.md` and
`results_meta/tasks/self_collision_transfer.json`.

## Preserved Scratch Notes

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
- matched OFF vs strict `phystwin` 302-frame comparison:
  - OFF `rmse_mean = 0.009786468930542469`
  - strict `phystwin` `rmse_mean = 0.010103434324264526`
  - `Newton/phystwin_bridge/results/tmp_off_vs_phystwin_302_compare_20260401/compare_summary.json`
- parity support comparison video:
  - `Newton/phystwin_bridge/results/tmp_off_vs_phystwin_302_compare_20260401/parity_support_demo/parity_support_demo.mp4`
  - `formal_slide/meeting_2026_04_01/gif/self_collision_parity_support.gif`
- professor report:
  - `tmp/report/self_collision_professor_report_20260401/report.md`
  - `tmp/report/self_collision_professor_report_20260401/report.pdf`
- controller-spring diagnostic:
  - one-step `force_abs_max = 0.006733048971410349`
  - short-rollout `force_abs_max = 389.3789927564146`
  - `pass = false`
  - `Newton/phystwin_bridge/results/tmp_controller_spring_diag_v2/controller_spring_diagnostic.json`
- unstable case-3 vs case-4 diagnosis root:
  - `Newton/phystwin_bridge/results/self_collision_case3_vs_case4_diagnosis_20260404_162159_6cb033a`
- reproducibility fix root:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607`
  - repeated full-matrix reruns: `5`
  - ranking invariant across all five reruns
- stable follow-up root:
  - `Newton/phystwin_bridge/results/self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33`
  - stable first positive frame: `40`
  - stable first persistent positive frame: `107`
  - peak positive frame: `137`
- visual bundle root:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_visual_bundle_20260408_042645_00feebe`
- restart@137 diagnostic roots:
  - pre-isolation:
    - `Newton/phystwin_bridge/results/ground_contact_self_collision_restart137_matrix_20260408_063329_5548588`
  - post-isolation:
    - `Newton/phystwin_bridge/results/ground_contact_self_collision_restart137_matrix_20260408_070609_eb0d80b`
- post-isolation-fix full matrix root:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260408_070232_eb0d80b`
  - case 1 `rmse_mean = 0.009801863692700863`
  - case 2 `rmse_mean = 0.00962120946496725`
  - case 3 `rmse_mean = 0.009368138387799263`
  - case 4 `rmse_mean = 0.009410285390913486`
- pre-isolation full matrix root:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260404_140154_e11491a`
  - best case by `rmse_mean`:
    - `case_3_self_phystwin_ground_native`
- OFF regression remains acceptable:
  - `rmse_mean = 0.00476811733096838`
  - `Newton/phystwin_bridge/results/tmp_off_ground_regression_60_postsync/off_ground_regression60_rollout_report.json`
- rope OFF importer smoke still passes:
  - `rmse_mean = 1.4174155694490764e-05`
  - `Newton/phystwin_bridge/results/tmp_rope_off_smoke_30_postsync/rope_off_smoke30_rollout_report.json`

## Historical Reading

The preserved local notes support the same conclusion now stated more cleanly in
the active task surfaces:

- the `2 x 2` matrix ranking is reproducible
- the old large `case_3 > case_4` gap was heavily driven by hidden timing semantics
- the remaining blocker is broader rollout/controller parity, not reproducibility
