> status: active
> canonical_replacement: none
> owner_surface: `robot_rope_franka_semiimplicit_oneway`
> last_reviewed: `2026-04-04`
> review_interval: `14d`
> update_rule: `Update when the conservative claim boundary, promoted result meaning, or chosen Path A vs Path B decision changes.`
> notes: Refocused conservative task for a Newton-native SemiImplicit deformable rope interaction baseline.

# Task: Native Franka + Native Table + Bridged Rope Under SemiImplicit (One-Way Baseline)

## Question

Can the project present a truthful Newton-native baseline where a native Newton
Franka drives a bridged PhysTwin rope in a `SolverSemiImplicit` deformable
simulation, while keeping the claim conservative:

- robot -> rope one-way is acceptable
- robot-table physical blocking is out of scope
- self-collision parity is out of scope

## Scope Decision

For this task, the project explicitly de-scopes:

- articulated robot-table physical blocking
- full two-way robot <-> rope coupling
- self-collision parity with PhysTwin
- non-deformable-only interaction perfection

The working claim is:

`A native Newton Franka, in a native Newton tabletop scene, drives a PhysTwin-loaded rope in a SolverSemiImplicit deformable simulation, with geometry truth preserved and without claiming articulated physical blocking.`

## Preferred Path

- `Path A` preferred:
  - reuse the accepted direct-finger tabletop baseline
  - keep actual finger-box contact as the final proof surface
  - keep rope render thickness aligned with physical rope thickness
- `Path B` fallback only if Path A fails honestly:
  - reuse the promoted visible rigid tool baseline
  - label it explicitly as tool-mediated

## Current Lean

- Path A currently appears sufficient for this conservative claim.
- The accepted tabletop hero already provides:
  - native Franka
  - native table
  - bridged rope
  - readable one-way robot -> rope interaction
  - geometry-truth fixes for rope thickness and finger-box proof

## Current Decision

- Chosen path: `Path A`
- Authoritative conservative bundle:
  - `Newton/phystwin_bridge/results/robot_rope_franka_semiimplicit_oneway/candidates/20260404_215523_c12_samehistory_oneway`
- Why Path A passed:
  - it reuses the already accepted truthful c12 tabletop rollout
  - it keeps actual finger-box contact as the proof surface
  - it keeps rope render thickness aligned with physical thickness
  - it narrows the claim to a one-way SemiImplicit deformable baseline instead
    of strengthening it toward physical blocking or full two-way coupling

## Current Promoted Meaning

- Promoted path: `Path A` direct finger
- Promoted local artifact root:
  - `Newton/phystwin_bridge/results/robot_rope_franka_semiimplicit_oneway/BEST_RUN/`
- Registry entry:
  - `results_meta/tasks/robot_rope_franka_semiimplicit_oneway.json`
- Source rollout:
  - the accepted c12 tabletop hero rollout, re-bundled under a narrower claim
- Conservative interpretation:
  - this is a Newton-native robot + table + bridged rope baseline whose
    deformable interaction runs under `SolverSemiImplicit`
  - it accepts one-way robot -> rope interaction only
  - it does not claim articulated physical blocking, full two-way coupling, or
    self-collision parity

## Required Outputs

- new task/spec/plan/status chain
- explicit scope decision note
- `solver_audit.md`
- `geometry_truth_report.md`
- `multimodal_review.md`
- a truthful results_meta entry only after the conservative pass is fully documented

## Related Pages

- [robot_rope_franka_tabletop_push_hero.md](./robot_rope_franka_tabletop_push_hero.md)
- [robot_visible_rigid_tool_baseline.md](./robot_visible_rigid_tool_baseline.md)
- [robot_rope_franka_physical_blocking.md](./robot_rope_franka_physical_blocking.md)
