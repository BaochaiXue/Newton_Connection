# Status: Final Self-Collision Campaign

> Historical task family. Active canonical task: `self_collision_transfer`.  
> Migration path: use `tasks/status/self_collision_transfer.md` for current state and keep this file as the archived campaign log.

## 2026-03-30

- Campaign root created at `Newton/phystwin_bridge/results/final_self_collision_campaign_20260330_205935_4fdef39/`.
- Instruction chain read from root `AGENTS.md`, `Newton/phystwin_bridge/AGENTS.md`, and bridge docs/task pages.
- Waiting on mandatory subagent reports before mainline implementation decisions.

## 2026-03-31

- Previous campaign remains legacy only:
  - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260330_205935_4fdef39/`
  - it reached exactness + demo QC, but strict parity stayed blocked and used out-of-scope rope parity artifacts
- Fresh campaign root created:
  - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/`
- New run inherits the same hard scope:
  - cloth + box self-collision ON
  - strict self-collision parity
- Initial scaffold now records the missing referenced paths explicitly:
  - root `AGENTS.override.md`
  - repo-root `phystwin_bridge/AGENTS.md`
- Next checkpoint:
  - spawn the seven required sub-agents
  - inspect current bridge-side parity feasibility against the in-scope self-collision case

## 2026-03-31 Final State

- All required sub-agent report files now exist under:
  - `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/subagents/`
- Fresh exactness evidence generated:
  - `equivalence/verify_phystwin_self_collision_equivalence.json`
  - `pass = true`
  - `max_abs_dv = 1.1324882507324219e-06`
  - `median_rel_dv = 4.070106739010465e-08`
- Fresh cloth+box matrix generated under:
  - `matrix/`
  - final matrix markdown now explains why the provisional `native` scorer output is not the campaign decision
- Fresh cloth+box `phystwin` hero render generated under:
  - `selected_candidates/phystwin_topdown/`
  - promoted asset:
    - `selected/self_collision_on_cloth_box_phystwin.mp4`
  - final accepted QC:
    - `video_qc/phystwin_topdown_v3/video_qc.json`
- Fresh parity support comparison video generated under:
  - `parity/support_demo/parity_support_demo.mp4`
  - promoted asset:
    - `selected/parity_support_demo.mp4`
  - QC:
    - `video_qc/parity_support_v1/video_qc.json`
- Strict self-collision parity remains blocked on the in-scope cloth reference case:
  - `parity/strict_self_collision_parity_summary.json`
  - `rmse_mean = 0.025657856836915016`
  - `rmse_max = 0.11557811498641968`
  - `first30_rmse = 0.08319681137800217`
  - `last30_rmse = 0.014951111748814583`
- The blocker is now precise and documented in:
  - `BLOCKER_strict_self_collision_parity_bridge_rollout_mismatch.md`
- The April 1 editable slide source was updated and rebuilt:
  - `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
  - `formal_slide/meeting_2026_04_01/bridge_meeting_20260401.pptx`
