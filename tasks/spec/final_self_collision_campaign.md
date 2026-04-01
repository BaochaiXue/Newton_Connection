# Task Spec: Final Self-Collision Campaign

> status: historical
> canonical_replacement: `tasks/spec/self_collision_transfer.md`
> owner_surface: `self_collision_transfer`
> last_reviewed: `2026-04-01`
> notes: Historical campaign spec kept for traceability only; current self-collision work belongs to the canonical task.

## Goal

Execute a clean bridge-only campaign that:

1. proves Newton native collision / native self-collision are insufficient for the final claim,
2. validates bridge-side PhysTwin-style self-collision exactness at operator level,
3. produces a meeting-quality `cloth + box + self-collision ON` demo with final mode `phystwin`,
4. passes a strict parity gate at `1e-5` scale,
5. updates slides or produces a complete slides update pack.

## Hard Constraints

- Do not modify `Newton/newton/`.
- Restrict the final claim to:
  - cloth + box self-collision ON
  - strict self-collision parity
- Prefer patching existing bridge-side scripts over inventing a parallel framework.
- Video QC has veto power; no candidate MP4 may be selected before QC passes.
- Final self-collision mode must be `phystwin`.

## Campaign Root

- `Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/`

## Required Reports

- `subagents/repo_audit/report.md`
- `subagents/scope_guard/report.md`
- `subagents/native_failure/report.md`
- `subagents/phystwin_exactness/report.md`
- `subagents/parity/report.md`
- `subagents/video_qc/report.md`
- `subagents/slides/report.md`

## Required Final Assets

- `selected/self_collision_on_cloth_box_phystwin.mp4`
- `selected/parity_support_demo.mp4`
- `equivalence/verify_phystwin_self_collision_equivalence.json`
- `parity/strict_self_collision_parity_summary.json`
- `video_qc/final_video_qc_report.md`
- updated slides or `slides_update/`
