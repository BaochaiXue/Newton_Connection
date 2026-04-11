> status: historical
> canonical_replacement: `../../../tasks/status/bunny_penetration_force_diagnostic.md`
> owner_surface: `bunny_penetration_force_diagnostic`
> last_reviewed: `2026-04-11`
> review_interval: `90d`
> update_rule: `Historical scratch log only. Do not record new active state here.`
> notes: Archived detailed bunny-board rollout notes moved out of the active status page so the live task status can stay short and operational.

# Historical Status Log: bunny_penetration_force_diagnostic 2026-04-01

This file preserves the detailed rollout / deck-refresh chronology that
previously lived in the active status surface. The canonical current state now
lives in `tasks/status/bunny_penetration_force_diagnostic.md` and
`results_meta/tasks/bunny_penetration_force_diagnostic.json`.

## Preserved Timeline

### Attempt: `20260401_011336_realtime_allcolliding_2x2_v1`

- run root:
  - `results/bunny_force_visualization/runs/20260401_011336_realtime_allcolliding_2x2_v1`
- produced:
  - per-case OFF rollout artifacts for `box_control` and `bunny_baseline`
  - per-frame detector bundles
  - final board video:
    - `artifacts/collision_force_board/collision_force_board_2x2.mp4`
  - validator outputs:
    - `qa/report.json`
    - `qa/verdict.md`
- board-aware visual QA passed
- remaining semantic blocker at that time:
  - the detector / board path used `f_external_total` as penalty force without a per-target shape decomposition
  - both cases reported `first_force_contact_frame_index = 1`
  - both cases also reported near-global active-node counts immediately after start

### Promoted Run: `20260401_013500_realtime_allcolliding_2x2_v5`

- promoted run root:
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5`
- final board artifact:
  - `artifacts/collision_force_board/collision_force_board_2x2.mp4`
- detector semantics:
  - main node set:
    - `rigid_force_contact_mask = geom_contact_mask AND target_force_contact_mask`
  - target-only penalty force:
    - `f_external_total` from explicit re-evaluation with `add_ground_plane=False`
  - total force:
    - `f_internal_total + f_external_total + mass * gravity_vec`
- first-collision indices:
  - `box_control = 4`
  - `bunny_baseline = 4`
- validators:
  - `qa/report.json` -> `PASS`
  - `qa/verdict.md`
  - `scripts/validate_experiment_artifacts.py` -> `PASS`
- updated local-only pointer surfaces:
  - `results/bunny_force_visualization/LATEST_SUCCESS.txt`
  - `results/bunny_force_visualization/LATEST_ATTEMPT.txt`
  - `results/bunny_force_visualization/INDEX.md`

### Slide Update

- updated the `2026-04-01` meeting deck source so the bunny force-analysis
  section explicitly stated:
  - cloth total mass = `0.1 kg`
  - rigid target mass = `0.5 kg`
- applied to visible slide text:
  - `Result F2`
  - `Result F3`
- regenerated:
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
  - `formal_slide/meeting_2026_04_01/transcript.md`
  - `formal_slide/meeting_2026_04_01/transcript.pdf`
- exported single-panel mp4s from the canonical board under:
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board/panels/`

### GIF Quality Refresh

- raised bunny-board GIF generation from low deck defaults to a size-capped
  quality policy:
  - board preferred profile:
    - `1600 px`, `15 fps`, `224 colors`
  - panel preferred profile:
    - `960 px`, `15 fps`, `224 colors`
  - per-GIF budget:
    - `< 40 MB`
- updated:
  - `scripts/render_bunny_penetration_collision_board.py`
  - `scripts/export_bunny_collision_board_panels.py`
  - `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- regenerated:
  - canonical board GIF
  - four single-panel GIFs for the result bundle
  - four single-panel GIFs for the meeting deck

### GIF Delivery Split

- clarified delivery rule:
  - single `pptx` must stay `< 100 MB`
  - single `gif` must stay `< 40 MB`
- split GIF handling into two tiers:
  - publish GIFs in the promoted result bundle
  - smaller slide-local GIFs under `formal_slide/meeting_2026_04_01/gif/`

### Slow-Motion Supplement

- added a supplemental `4x` slow-motion bunny `2 x 2` board under:
  - `results/bunny_force_visualization/runs/20260401_013500_realtime_allcolliding_2x2_v5/artifacts/collision_force_board_slow4x/`
- artifacts:
  - publish mp4:
    - `collision_force_board_2x2_slow4x.mp4`
  - publish gif:
    - `collision_force_board_2x2_slow4x.gif`
  - summary:
    - `summary.json`
- slide deck update:
  - added `Result F4`
  - regenerated the `2026-04-01` deck and transcript
