> status: canonical
> canonical_replacement: none
> owner_surface: `bridge_control_plane`
> last_reviewed: `2026-04-04`
> review_interval: `30d`
> update_rule: `Update when an open question is answered, superseded, or promoted into a dedicated task or decision surface.`
> notes: Canonical unresolved-question ledger for bridge work. Keep resolved items out of this page.

# Open Questions

Last updated: 2026-04-04

This page records unresolved bridge questions that still matter technically.

## Contact / Penetration

- In bunny failure cases, is the dominant issue:
  - wrong effective outward direction near sharp geometry?
  - insufficient normal contact magnitude?
  - internal force / inertia dominating contact response?
  - some combination of the above?
- Does the cloth-side force diagnostic generalize to rope-side failure cases?
- How much of the bunny failure is geometry-specific vs parameter-specific?

## Performance

- After the rope apples-to-apples benchmark, how much of the remaining Newton
  gap is specifically due to lack of graph-captured replay versus kernel-level
  solver cost?
- Can Newton rope replay move closer to PhysTwin headless throughput after
  bridge precompute + more batched execution, without changing `dt/substeps`?
- For the interactive playground, what fraction of wall time is due to:
  - collision generation
  - decoupled multi-kernel stepping overhead
  - viewer/render path
  - diagnostics/instrumentation overhead
- Can a bridge-side path achieve convincing real-time behavior on the target demo
  classes without changing Newton core?

## Self-Collision

- Which controlled box-matrix result will win:
  - native enough
  - custom filtered penalty enough
  - bridge-side PhysTwin-style needed
- After localizing the stable `case_3 > case_4` ordering to whole-step
  interaction plus controller-spring semantics mismatch, what is the smallest
  bridge-side fix that actually lets the fully PhysTwin-style pair overtake the
  native-ground compensating path?
- Can the remaining controller-spring mismatch be reduced without changing
  Newton core, or has the task reached a genuine bridge-layer limit?
- Can we add peak-over-time overlap metrics so the self-collision decision is
  not based only on final-frame statistics?
- After choosing a self-collision path, does the same choice remain compatible
  with bunny rigid-contact sanity checks and the current OFF-baseline parity path?

## Robot + Deformable

- Which robot/deformable interaction is the best meeting-quality demo:
  - robot pushes rope
  - robot manipulates cloth
  - robot interacts with rigid-supported deformable

## Native Rope Drop Baseline

- In the promoted 5 kg baseline, drag OFF and drag ON both keep the early
  free-fall acceleration close to `g`; the remaining question is whether later
  variants should keep drag OFF for clearer support/release storytelling or ON
  for softer impact and settling.
- Can the release mechanism stay simple enough that the robot is visually
  present but not the main story after `t_release`?

## Data / Reconstruction

- What exact capture protocol should become the default for new PhysTwin data?
- Can Fast-FoundationStereo replace the current RealSense depth path on the
  cases we actually care about?

## Documentation

- Which bridge behaviors should be promoted from local script knowledge into
  stable encyclopedia pages?
- Which experimental outputs deserve a hard artifact contract?

## Harness / Workflow

- Have we actually validated the new repo-local Codex control plane
  (`.codex/config.toml`, hooks, subtree `AGENTS.md`, repo-local skills) in a
  fresh trusted Codex session, rather than only by static parsing?
- Which current workflows still lack canonical wrappers and therefore force
  agents back into ad hoc shell commands?
- Which task types should always require:
  - a task page
  - a plan file
  - a task status log
  and which ones are still small enough to stay lightweight?
- Which validator checks should become hard gates for “done”, and which should
  remain advisory?
- How should legacy experiment directories under `tmp/` be migrated:
  - backfill them to the new contract
  - keep them as historical exceptions
  - or archive them outside the main working set?
