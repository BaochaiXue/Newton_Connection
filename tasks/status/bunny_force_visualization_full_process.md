# Status: Bunny Force Visualization Full Process

## 2026-03-30

- task scaffold created for the stricter full-process bunny visualization push
- current known blocker: the split helper workflow was bypassing the object-only
  OFF IR path, which caused a bogus substep-0 trigger on the new baseline run
- current work:
  - patch split wrapper to use `_copy_object_only_ir(...)`
  - rerender `bunny_baseline`
  - validate against the stricter duration and visibility gates

## 2026-03-31

- `scripts/run_bunny_force_case.py` now matches the object-only OFF path used by
  `demo_cloth_bunny_drop_without_self_contact.py`
- the force mechanism renderer now prefers the stable phenomenon-frame overlay
  path instead of relying on a second force-only viewer render
- accepted strict baseline bundle:
  - `results/bunny_force_visualization/runs/20260331_033500_baseline_syncfix_v1`
- accepted baseline checks:
  - phenomenon duration `4.97s`
  - force duration `4.97s`
  - `validate_bunny_force_visualization.py` -> `PASS`
  - `validate_experiment_artifacts.py` -> `PASS`
- accepted full 4-case canonical bundle:
  - `results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2`
- final package checks:
  - `summary.json` contains 4 cases, all `PASS`
  - `bunny_penetration_summary_board.png` exists
  - every case now has `force_diag_trigger_window_mapping.json`
  - all four cases report:
    - `exact_mapping_ratio_active_interval = 1.0`
    - `reused_mapping_ratio_active_interval = 0.0`
  - `LATEST_SUCCESS.txt` and `INDEX.md` now point at the accepted sync-safe run
