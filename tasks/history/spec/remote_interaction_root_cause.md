> status: historical
> canonical_replacement: `../../../docs/decisions/2026-04-09_robot_ps_interaction_retirement.md`
> owner_surface: `remote_interaction_root_cause`
> last_reviewed: `2026-04-09`
> notes: Historical completed spec archived out of `tasks/spec/`.

# Spec: remote_interaction_root_cause

## Goal

Diagnose and eliminate the apparent stand-off / remote-interaction behavior in
the tabletop hero so the visible Franka finger itself clearly contacts and
drives the rope.

## Non-Goals

- Newton core changes under `Newton/newton/`
- blind parameter sweeps without evidence
- declaring success from automatic QC alone
- changing the chapter claim to something weaker instead of fixing the cause

## Inputs

- current promoted tabletop hero code path
- current promoted run bundle under
  `Newton/phystwin_bridge/results/robot_rope_franka/`
- current wrapper, validator, and registry metadata
- full hero/debug/validation videos and rollout histories

## Outputs

- repo-native task scaffolding and live status
- evidence-backed hypothesis board
- ranked root-cause report
- targeted code fix
- new validated candidate bundle
- promoted run update only if every gate passes

## Constraints

- `Newton/newton/` is read-only
- no hidden helper or invisible physical influencer
- keep the robot native to Newton
- keep the table native to Newton
- keep the rope on the PhysTwin -> Newton bridge
- use the current repository state as the source of truth

## Done When

- diagnosis, fix, rerun, validation, and multimodal review all pass
- no remaining remote-interaction impression remains
- docs, task status, and results metadata reflect the new state
