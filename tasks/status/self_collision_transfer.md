> status: active
> canonical_replacement: none
> owner_surface: `self_collision_transfer`
> last_reviewed: `2026-04-11`
> review_interval: `21d`
> update_rule: `Update when the committed blocked surface, active blocker, or next mechanism step changes. Move long scratch notes into historical logs instead of expanding this page indefinitely.`
> notes: Active operational status for the self-collision transfer task. Keep this file short and point detailed historical diagnostics elsewhere.

# Status: self_collision_transfer

## Current State

This task remains active and blocked.

Committed current-bundle meaning lives in:

- `results_meta/tasks/self_collision_transfer.json`

Current high-confidence state:

- the fair cloth+implicit-ground `2 x 2` matrix ranking is reproducible
- the old large `case_3 > case_4` gap was mostly driven by hidden whole-step timing differences
- after the explicit ground-law isolation fix, the remaining blocker is the broader controller-spring / rollout parity mismatch
- strict `phystwin` scope remains intentionally narrow:
  - pairwise self-collision
  - implicit `z=0` ground law
  - not generic box-support contact

## Current Evidence Roots

- committed blocked surface:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607`
- post-isolation-fix full matrix:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260408_070232_eb0d80b`
- post-isolation-fix restart@137 continuation matrix:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_restart137_matrix_20260408_070609_eb0d80b`
- stable case-3-vs-case-4 follow-up:
  - `Newton/phystwin_bridge/results/self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33`
- stable visual bundle:
  - `Newton/phystwin_bridge/results/ground_contact_self_collision_visual_bundle_20260408_042645_00feebe`

Historical scratch detail moved out of the active page:

- `tasks/history/status/self_collision_transfer_diagnostic_log_20260401_20260408.md`

## Last Completed Step

The last meaningful milestone was the explicit ground-law isolation fix plus the
follow-up reruns:

- native and PhysTwin-style ground branches now share the same pre-self velocity semantics in the controlled matrix path
- the old large `case_3 > case_4` gap collapsed from about `1.64e-3` to about `4.21e-5`
- restart@137 continuation reruns show native-ground and PhysTwin-style-ground become numerically indistinguishable after that isolation fix

That means the old headline gap is no longer the main blocker.

## Next Step

- keep the reproducible matrix root as the committed blocked surface
- treat the post-isolation matrix and restart@137 roots as the current local mechanism evidence
- if a future bridge-side fix is attempted, compare it against:
  - the reproducible matrix root
  - the post-isolation matrix root
  - the restart@137 root
- only promote a new root into `results_meta` if it actually changes the stable blocked surface or closes the remaining parity blocker

## Blocking Issues

- the fair `2 x 2` matrix still misses the strict `1e-5` gate in all four cases
- controller-spring semantics mismatch still reports a large force gap
- the remaining blocker is now broader rollout parity, not reproducibility
- strict `phystwin` still does not cover box or other Newton-only rigid-support contacts

## Artifact Paths

- `results_meta/tasks/self_collision_transfer.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607/final_verdict.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_repro_fix_20260404_200830_aa5e607/repro_audit_summary.md`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_rmse_matrix_20260408_070232_eb0d80b/rmse_matrix_summary.json`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_restart137_matrix_20260408_070609_eb0d80b/rmse_matrix_summary.json`
- `Newton/phystwin_bridge/results/self_collision_transfer_case3_vs_case4_followup_20260404_210334_ac9ec33/final_recommendation.md`
- `Newton/phystwin_bridge/results/ground_contact_self_collision_visual_bundle_20260408_042645_00feebe/README.md`
