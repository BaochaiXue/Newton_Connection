> status: historical
> canonical_replacement: `../../bridge/tasks/robot_rope_franka_tabletop_push_hero.md`
> owner_surface: `remote_interaction_root_cause`
> last_reviewed: `2026-04-09`
> review_interval: `90d`
> update_rule: `Historical evidence only. Do not record new operating state here.`
> notes: Archived root-cause record for the c12 tabletop-hero truth fix.

# Task: Remote-Interaction Root Cause In The Tabletop Hero

## Question

Why does the current tabletop hero sometimes look like the visible Franka finger
has not touched the rope yet while the rope already reacts?

## Why It Matters

The tabletop hero only supports a meeting-facing robot-deformable claim if the
visible Franka finger itself appears to cause the rope motion. If the clip
looks like stand-off interaction, the current chapter claim is no longer
defensible even if automatic validation passes.

## Current Status

- Historical on `2026-04-09`.
- Completed on `2026-04-01`.
- Winning replacement run:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_203416_remotefix_truthcam_c12`
- Root-cause conclusion:
  - no hidden helper
  - no Newton-core bug evidence
  - primary issue was a visual-truth mismatch: the old tabletop hero rendered
    the rope much thinner than the physical rope collision thickness
  - secondary contributors were proxy semantics (`finger_span`) and hero-camera
    ambiguity
- This task exists to preserve the evidence bundle backing that conclusion.

## Code Entry Points

- Main demo:
  - `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py`
- Canonical wrapper:
  - `scripts/run_robot_rope_franka_tabletop_hero.sh`
- Canonical validator:
  - `scripts/validate_robot_rope_franka_hero.py`
- Promoted run registry:
  - `results_meta/tasks/robot_rope_franka_tabletop_push_hero.json`

## Canonical Commands

- `bash scripts/run_robot_rope_franka_tabletop_hero.sh --tag <tag>`
- `python scripts/validate_robot_rope_franka_hero.py <RUN_DIR> --manual-review-json <RUN_DIR>/manual_review.json`

## Required Artifacts

- diagnostic board:
  - `diagnostics/remote_interaction_hypothesis_board.md`
- ranked root-cause report:
  - `diagnostics/root_cause_ranked_report.md`
- geometry / control / proxy / camera reports:
  - `diagnostics/*.md`
  - `diagnostics/*.json`
  - `diagnostics/*.csv`
- candidate bundle:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/<RUN_ID>/...`

## Success Criteria

- root cause is ranked with evidence, not guessed
- no hidden helper influences the visible clip
- the visible Franka finger itself is the believable contactor
- rope deformation and lateral motion begin after visible finger contact
- no obvious remote-interaction impression remains in full-video review
- new bundle passes validator and truthful manual review
- the promoted run metadata is updated only after that pass

## Open Questions

- Is the problem mainly actual contact geometry, diagnostic proxy logic, or a
  control-reference mismatch?
- Is the current rope thickness itself visually too large for the tabletop
  claim?
- Does the hero camera exaggerate a real but visually ambiguous contact?

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](../../bridge/tasks/robot_rope_franka_tabletop_push_hero.md)
- [video_presentation_quality.md](../../bridge/tasks/video_presentation_quality.md)
