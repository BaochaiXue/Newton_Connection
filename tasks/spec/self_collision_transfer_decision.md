# Spec: self_collision_transfer_decision

## Goal

Turn self-collision into a controlled bridge-side decision task and produce one
explicit conclusion:

- A. native Newton is enough
- B. bridge-side custom filtered penalty is enough
- C. bridge-side PhysTwin-style self-collision is needed

## Non-Goals

- full PhysTwin parity for every collision behavior
- modifying `Newton/newton/`
- deciding from bunny-only evidence
- relying only on final-frame overlap statistics

## Inputs

- `Newton/phystwin_bridge/demos/demo_cloth_box_drop_with_self_contact.py`
- `Newton/phystwin_bridge/demos/self_contact_bridge_kernels.py`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`
- `Newton/phystwin_bridge/demos/demo_cloth_bunny_realtime_viewer.py`
- `Newton/phystwin_bridge/tools/core/validate_parity.py`
- current strict cloth IR defaults

## Outputs

- rollout-peak self-overlap metrics in box self-contact summaries
- matrix runner under `Newton/phystwin_bridge/tools/other/`
- operator-equivalence verifier for bridge-side PhysTwin-style self-collision
- decision artifacts:
  - `self_collision_decision_table.csv`
  - `self_collision_decision.md`
  - comparison figure
  - selected-mode MP4

## Constraints

- keep the main decision scene as cloth-on-fixed-box
- do not modify `Newton/newton/`
- treat thresholds as provisional defaults
- require operator-level equivalence evidence before allowing conclusion C

## Done When

- box decision matrix runs for `off/native/custom_h1/custom_h2/phystwin`
- summaries include rollout-peak overlap metrics
- matrix runner emits CSV + markdown + figure
- PhysTwin-style operator verifier emits JSON with pass/fail
- one selected candidate can be passed into bunny sanity check + profiler
