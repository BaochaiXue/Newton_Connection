# Root Cause Ranked Report

Last updated: 2026-04-03

## Ranked Hypotheses

1. **H1. The current tabletop controller is effectively kinematic / state-overwriting**
   - confidence: high
   - evidence:
     - direct `state_in.joint_q/joint_qd` writes before `solver.step()`
     - direct `state_out.joint_q/joint_qd` writes after `solver.step()`
     - near-zero target-tracking error during large table penetration in
       `c20_clean`

2. **H2. Joint targets and gains exist, but the direct assignment path wins**
   - confidence: high
   - evidence:
     - builder sets `joint_target_pos/ke/kd`
     - runtime tabletop path never passes a meaningful `control` object into
       the semi-implicit solve

3. **H5. The promoted tabletop task was never intended to claim physically blocked robot motion**
   - confidence: high
   - evidence:
     - task page and results metadata describe a readable baseline, not blocked
       robot actuation
     - accepted `c12` does not even contact the table in the new blocking audit

4. **H3. Robot-table collisions may exist but are not enough to stop the hand**
   - confidence: medium
   - evidence:
     - table box and URDF finger boxes are present
     - collision generation is called
     - but state overwrite makes it impossible to conclude solver contacts are
       ineffective by themselves

5. **H4. Gains may be too stiff after actuation becomes honest**
   - confidence: medium
   - evidence:
     - likely secondary issue once direct overwrite is removed

## Explicit Answers

1. Is the current tabletop path physically actuated or effectively kinematic?
   - effectively kinematic
2. Is table penetration caused primarily by state overwrite / control semantics?
   - yes
3. Are actual robot-table collisions present but being numerically overpowered?
   - possibly, but not the primary root cause
4. Is there any hidden helper?
   - no
5. Can this be fixed at bridge/demo level without touching `Newton/newton/`?
   - likely yes; the interface surface exists via `model.control()` and solver
     drive terms, but it still needs to be implemented and validated
