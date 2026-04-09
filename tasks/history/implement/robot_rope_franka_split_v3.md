> status: historical
> canonical_replacement: `../../../docs/bridge/tasks/robot_rope_franka_physical_blocking.md`
> owner_surface: `robot_rope_franka_split_v3`
> last_reviewed: `2026-04-09`
> notes: Historical exploratory runbook archived out of `tasks/implement/`.

# Implement: robot_rope_franka_split_v3

## First Required Outputs

- `diagnostics/split_v3_native_demo_lessons.md`
- `diagnostics/split_v3_architecture_decision.md`
- `diagnostics/split_v3_final_causal_account.md`

## Next Required Code

- new split-v3 demo entrypoint
- new split-v3 wrapper
- Stage-0 candidate bundle
- Stage-1 candidate bundle

## Guardrails

- no edits under `Newton/newton/`
- do not reuse overwrite semantics
- do not let v2 become the final route by inertia
