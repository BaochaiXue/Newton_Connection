# Robot Rope Franka Physical Blocking Diagnosis Board

Last updated: 2026-04-03

| Hypothesis | Evidence For | Evidence Against | Required Instrumentation | Likely Fix | Confidence |
| --- | --- | --- | --- | --- | --- |
| H1. Current tabletop path is effectively kinematic | `demo_robot_rope_franka.py` writes `state_in.joint_q/joint_qd` before `solver.step()` and writes `state_out.joint_q/joint_qd` again after `solver.step()` in `joint_trajectory` mode; `c19` shows severe table penetration with near-zero target error | none yet | control update-order report; target-vs-actual lag under table contact | remove state overwrite from the stronger path; drive the articulation through `control.joint_target_pos` instead | high |
| H2. Joint targets exist but are bypassed by direct state writes | builder already sets `joint_target_pos/ke/kd`; Newton docs/examples show SemiImplicit supports joint targets through `model.control()`; current promoted path passes `None` as control | none yet | code audit plus minimal joint-drive candidate | use `model.control()` and pass it to `solver.step()`; stop snapping post-solve state | high |
| H3. Robot-table collisions are missing or filtered out | none so far; table box exists and finger colliders exist | current audit shows `tabletop_table_box` is present as a world box and finger box colliders exist on both fingers | collider inventory; robot-table clearance timeseries | unlikely primary fix | low |
| H4. Collisions exist but controller stiffness overwhelms them | possible secondary issue after state-overwrite removal | current `c19` evidence is stronger for outright kinematic overwrite than for a merely too-stiff drive | blocking candidate with articulation targets, then inspect penetration and target lag | retune gains / speed limits only after honest actuation exists | medium |
| H5. Old promoted task used the wrong success criteria for blocking | old task page explicitly claims only a readable tabletop baseline, not physical blocking | none | separate stronger task chain and results registry | keep old baseline authority; document new stronger task separately | high |
| H6. More than one hypothesis is true | likely H1/H2 + possibly H4 | none | full root-cause report after first blocking candidate | layered fix: actuation semantics first, gain retune second | high |
