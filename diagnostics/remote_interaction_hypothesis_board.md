# Remote Interaction Hypothesis Board

Last updated: 2026-04-01

This board must be updated before any behavior-changing fix is accepted.

| Hypothesis | Evidence For | Evidence Against | Confidence | Required Instrumentation | Potential Fix |
| --- | --- | --- | --- | --- | --- |
| H1. Hidden helper / invisible physical influencer exists | none yet | current code path visibly uses native URDF + table + rope path; no helper body found yet | low | enumerate active bodies/shapes/constraints during visible clip | remove helper or neutralize it |
| H2. Actual URDF collision geometry and visible mesh are misaligned enough to create apparent stand-off contact | finger collision uses several box colliders, not a point contactor | no direct overlay yet | medium | collider inventory + collider overlay render | align claim/camera/control with actual contact geometry |
| H3. Tabletop control reference point is wrong | tabletop path targets abstract link-space / gripper-center-style references in some modes | promoted path is joint-trajectory, not raw IK target chasing | medium | target-point overlay + target-to-visible-finger offset | switch to fingertip / finger-pad reference |
| H4. Diagnostic proxy geometry is too thick / finger_span dominates | current summary says `contact_proxy_counts = {finger_span: 88}` and proxy radius is thick | proxy path may only affect diagnosis, not solver contact | high | per-frame proxy onset vs actual visible contact | downgrade or remove finger_span as success evidence |
| H5. Rope particle collision thickness is too large | current rope collision radius is about 0.026 m, visually thick for a tabletop rope | may still be acceptable if collider overlay makes it honest | high | rope thickness audit + scale summary | reduce thickness only if justified and documented |
| H6. Positive tabletop clearances + motion path keep real geometry above rope while diagnostics imply contact | current path uses explicit tabletop clearances and joint-space waypoints | promoted run still shows some rope response and negative proxy clearance | medium | per-frame finger/rope/tip distance timeline | reduce clearances or retarget the contact point |
| H7. Camera / presentation ambiguity makes true contact look fake | user report and current hero angle both suggest ambiguity | validation view may already be clearer | medium | contact-patch visibility scoring + full-video review | move hero camera after geometry is truthful |
| H8. Multiple causes are simultaneously true | current evidence already points to proxy thickness + rope thickness + view ambiguity | final ranking not done yet | high | combined root-cause report | fix primary cause first, then secondary contributors |
