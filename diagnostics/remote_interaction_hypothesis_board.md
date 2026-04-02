# Remote Interaction Hypothesis Board

Last updated: 2026-04-01

This board must be updated before any behavior-changing fix is accepted.

| Hypothesis | Evidence For | Evidence Against | Confidence | Required Instrumentation | Potential Fix |
| --- | --- | --- | --- | --- | --- |
| H1. Hidden helper / invisible physical influencer exists | none yet | current code path visibly uses native URDF + table + rope path; no helper body found yet | low | enumerate active bodies/shapes/constraints during visible clip | remove helper or neutralize it |
| H2. Actual URDF collision geometry and visible mesh are misaligned enough to create apparent stand-off contact | actual contact occurs on `left_box_3`, the real fingertip collision box, while the viewer sees the visual mesh rather than raw colliders | the real contactor is still the visible finger link, not a hidden helper | medium-high | collider inventory + collider overlay render | align visible proof with actual fingertip contact patch |
| H3. Tabletop control reference point is wrong | promoted joint-trajectory path reports `ee_target_pos` as gripper center; mean target-to-nearest fingertip-center offset is about `0.0657 m` | the joint-space path still produces real fingertip contact | medium | target-point overlay + target-to-visible-finger offset | report / visualize fingertip contact rather than centerline target |
| H4. Diagnostic proxy geometry is too thick / finger_span dominates | current summary says `contact_proxy_counts = {finger_span: 88}` and proxy radius is `0.033 m` | actual fingertip collider contact occurs earlier than `finger_span`, so proxy is not the primary physical cause | medium | per-frame proxy onset vs actual-collider onset | downgrade or remove finger_span as main proof surface |
| H5. Rope particle collision thickness is too large | rope physical collision radius is about `0.026 m`, render radius is capped to `0.004 m`, and rope diameter exceeds fingertip half-thickness by about `2.8x` to `3.4x` | none strong so far; this is the best-supported physical/visual mismatch | very high | rope thickness audit + render-thickness comparison | make rope rendering honest first; only then consider changing physics thickness |
| H6. Positive tabletop clearances + motion path keep real geometry above rope while diagnostics imply contact | joint-space path uses centerline semantics and explicit clearances | actual fingertip box still reaches contact before rope motion onset | low-medium | per-frame finger/rope/tip distance timeline | only retune after visual truth is fixed |
| H7. Camera / presentation ambiguity makes true contact look fake | hero shot is more ambiguous than validation shot around the left-finger contact patch | camera is a contributor, not the earliest-contact cause | medium | contact-patch visibility scoring + full-video review | retarget hero after contact geometry is made visually honest |
| H8. Multiple causes are simultaneously true | current evidence already points to proxy thickness + rope thickness + view ambiguity | final ranking not done yet | high | combined root-cause report | fix primary cause first, then secondary contributors |
