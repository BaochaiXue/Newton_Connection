# Newton Section

This section explains Newton from the point of view of the current project.

## Scope

Newton appears in this repository in two different senses:

- the upstream Newton simulator core under `Newton/newton/`
- the project-specific bridge code under `Newton/phystwin_bridge/`

This section is about the first one: the simulator/runtime we are integrating
with. The bridge-specific logic is documented separately under `docs/bridge/`.

## Workspace Rule

In this workspace:

- `Newton/newton/` is read-only

So Newton pages are explanatory and analytical. Project-side implementation
changes should not be documented here as if they were Newton core changes.

## Start Here

- [architecture.md](./architecture.md)
- [runtime_and_contacts.md](./runtime_and_contacts.md)
- [robot_example_patterns.md](./robot_example_patterns.md)

## Why This Section Exists

Many project questions depend on Newton concepts:

- body vs shape
- solver choice
- contact model
- viewer/runtime behavior
- how to interpret source-level kernels without editing them

These pages should make those concepts easier to explain without mixing them
with bridge-specific glue.

## Related Pages

- [../bridge/README.md](../bridge/README.md)
- [../bridge/demos_and_diagnostics.md](../bridge/demos_and_diagnostics.md)
