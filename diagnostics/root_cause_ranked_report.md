# Root Cause Ranked Report

Investigated run: `/home/xinjie/Newton_Connection/Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN`

## Ranked Hypotheses

1. H8 combination case
   Primary contributors are H5 rope thickness vs render mismatch, H7/H2 presentation ambiguity around the real fingertip collider, and H3 centerline-style control/reference semantics.
2. H5 rope particle collision thickness plus render mismatch is large
   Rope collision radius is `0.026002 m`, but render-only particle radius is capped to `0.004 m`, so the visible rope is only about `15.4%` of the physical contact radius.
3. H2 URDF collider vs visual mesh mismatch is real and matters
   Actual first solver-like contact occurs on `left_box_3`, the real fingertip collision box, while the viewer sees the visual mesh rather than the raw box colliders.
4. H7 camera / presentation contributes
   The hero view is more ambiguous than the validation view around the contact patch.
5. H3 control-reference semantics are mismatched with the visible claim
   The promoted joint-trajectory path reports a gripper-center target rather than a fingertip target, with about `0.0657 m` mean offset to the nearest fingertip center.
6. H4 diagnostic / proxy geometry is too aggressive
   Current summary reports only `finger_span` contact counts: `{'finger_span': 88}`, but actual fingertip-box contact occurs earlier than the proxy onset, so this is a truth-surface problem more than the primary physical cause.
7. H1 hidden helper exists
   Rejected. No hidden physical influencer was found in the visible tabletop clip path.

## Primary Root Cause

The current remote-interaction impression is primarily a bridge/demo-layer visual-truth issue, not a Newton core failure.
The strongest concrete mismatch is that the rope physically collides as a `0.026 m`-radius particle cloud, while the tabletop render path caps the visible particle radius to `0.004 m`. The actual fingertip collision box therefore reaches the rope before the visible rope looks thick enough, and the hero camera plus centerline-style diagnostics amplify that ambiguity.

## Newton Core Verdict

No evidence currently points to Newton core itself as the primary culprit.

## Hidden Helper Verdict

`hidden_helper_exists = false`
`hidden_helper_affects_visible_clip = false`

## Targeted Fix Direction

1. Make the rope rendering honest to the physical rope collision thickness first.
2. Keep the visible contactor as the real fingertip / finger pad and demote `finger_span` to auxiliary diagnostics only.
3. Retarget the hero framing to show the fingertip contact patch more directly.
4. Revisit actual rope physics thickness only if the stand-off feeling remains after the visual-truth fix.
