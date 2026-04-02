> status: active
> canonical_replacement: none
> owner_surface: `remote_interaction_root_cause`
> last_reviewed: `2026-04-01`
> review_interval: `7d`
> update_rule: `Update when the root-cause ranking, fix direction, or accepted evidence bundle changes.`
> notes: This task is a focused fail-closed investigation on the tabletop hero's apparent stand-off contact / remote-interaction problem.

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

- Active root-cause investigation started on `2026-04-01`.
- The current promoted tabletop run remains:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260401_093102_fixeddt_c10_contactfix_cam`
- Early evidence already suggests the issue may be a combination of:
  - thick rope collision radius,
  - aggressive diagnostic proxies,
  - control-reference / visible-finger mismatch,
  - and presentation-layer ambiguity.
- This task does not assume the cause; it exists to rank and prove it.

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

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [video_presentation_quality.md](./video_presentation_quality.md)
