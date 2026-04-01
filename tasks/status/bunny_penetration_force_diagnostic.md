# Status: Bunny Penetration Force Diagnostic

## 2026-03-30

- Re-opened under stricter full-process criteria.
- Confirmed the old short trigger-centric run is no longer acceptable.
- Found one concrete orchestration bug:
  the helper wrapper looked for `phenomenon/self_off/force_diagnostic/force_render_bundle.pkl`,
  but the bundle is actually written to `phenomenon/force_diagnostic/force_render_bundle.pkl`.
- Started a baseline-only full-process run:
  `results/bunny_force_visualization/runs/20260331_011500_baseline_fullprocess_v2`
- Phenomenon side reached a 5.16s process video; force side is being revalidated
  from the deferred bundle before propagating changes to the full matrix.

## Next Step

- finished the accepted strict-sync `bunny_baseline` under:
  `results/bunny_force_visualization/runs/20260331_033500_baseline_syncfix_v1`
- rebuilt the full 4-case matrix under:
  `results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2`
- confirmed all four force videos now satisfy the synchronization gate:
  - `exact_mapping_ratio_active_interval = 1.0`
  - `reused_mapping_ratio_active_interval = 0.0`
- updated canonical result pointers and index to the new sync-safe run

## 2026-04-01

- A new visualization change request was added under the same bunny task:
  - stop focusing on top-k probes only
  - render all rigid-contact cloth nodes on every displayed frame
  - produce a self-collision-OFF `2 x 2` board:
    - box penalty
    - box total
    - bunny penalty
    - bunny total
- Chosen implementation path:
  - keep using `demo_cloth_bunny_drop_without_self_contact.py` for both
    `--rigid-shape box` and `--rigid-shape bunny`
  - add a new board renderer:
    `scripts/render_bunny_penetration_collision_board.py`
  - add a canonical wrapper:
    `scripts/run_bunny_penetration_collision_board.sh`
- Pending at this checkpoint:
  - smoke-run the new wrapper
  - verify the shell wrapper argument handling and the board renderer on a real
    bundle
  - keep the standard support setup because removing the ground plane caused the
    bunny baseline to miss contact entirely during smoke testing
