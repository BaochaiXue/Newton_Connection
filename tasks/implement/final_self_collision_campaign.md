# Runbook: Final Self-Collision Campaign

## Campaign Root

- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/`

## Main Steps

1. Collect required subagent reports under `subagents/`.
2. Add/patch bridge-side orchestration and generalized video QC tooling.
3. Run:
   - controlled self-collision matrix
   - strict exactness verifier
   - strict self-collision parity validator or wrapper
4. QC all candidate MP4s.
5. Promote only QC-passing assets into `selected/`.
6. Update the editable April 1 slide source or generate a full slide replacement pack.
7. Validate artifact directories and update `manifest.json` + final status outputs.

## Candidate Commands

- matrix:
  - `python Newton/phystwin_bridge/tools/other/run_self_collision_matrix.py ...`
- equivalence:
  - `python Newton/phystwin_bridge/tools/other/verify_phystwin_self_collision_equivalence.py ...`
- strict parity:
  - `python Newton/phystwin_bridge/tools/core/validate_parity.py ...`
  - or a bridge-side strict self-collision parity wrapper under `tools/other/`

## Hard Gates

- no Newton core edits
- native insufficiency evidence complete
- strict exactness pass
- final cloth-box phystwin demo QC pass
- strict parity pass
- slides updated or full slides update pack exists
