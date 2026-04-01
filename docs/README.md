# PhysTwin -> Newton Project Encyclopedia

This `docs/` tree is the long-lived knowledge base for the current project.
It is not meant to be a one-off note dump. It should answer three questions:

1. What does each subsystem do?
2. Where is the code that implements it?
3. What do we currently believe, know, and still need to verify?

## Design Principles

- Concept first, code second.
- Each page should be readable by a new student and still useful to the current implementer.
- Every topic should connect abstract ideas to concrete file paths.
- Hypotheses, diagnostics, and open questions should be recorded explicitly.
- The documentation should reflect the current local project, not only upstream repos.

## Information Architecture

This encyclopedia is split into three layers:

- `phystwin/`
  - What PhysTwin is in this project.
  - What data/products it exports.
  - How those products become inputs to the bridge.
- `newton/`
  - What Newton provides as the simulator/runtime.
  - Which Newton concepts matter to this project.
  - Which parts of Newton are treated as read-only source.
- `bridge/`
  - The actual project-specific integration layer.
  - IR export/import.
  - Demos, diagnostics, viewers, experiments, and research logic.

Supporting harness sections:

- `runbooks/`
  - reusable operational instructions
- `evals/`
  - evaluator rubrics and validation standards
- `decisions/`
  - durable decision records
- `generated/`
  - machine-generated docs or indexes that should still live in-repo

There are also two cross-cutting pages:

- [PROJECT_MAP.md](./PROJECT_MAP.md)
- [STYLE_GUIDE.md](./STYLE_GUIDE.md)
- [bridge/current_status.md](./bridge/current_status.md)
- [bridge/open_questions.md](./bridge/open_questions.md)

## Reading Paths

If you are new to the project:

1. Read [PROJECT_MAP.md](./PROJECT_MAP.md)
2. Read [bridge/README.md](./bridge/README.md)
3. Read [phystwin/README.md](./phystwin/README.md)
4. Read [newton/README.md](./newton/README.md)
5. Read [runbooks/local_dev.md](./runbooks/local_dev.md)

If you are debugging bridge behavior:

1. Read [bridge/architecture.md](./bridge/architecture.md)
2. Read [bridge/ir_and_import.md](./bridge/ir_and_import.md)
3. Read [bridge/demos_and_diagnostics.md](./bridge/demos_and_diagnostics.md)
4. Read [bridge/tasks/README.md](./bridge/tasks/README.md)

If you are preparing slides or answering mechanism questions:

1. Read [bridge/demos_and_diagnostics.md](./bridge/demos_and_diagnostics.md)
2. Read [newton/runtime_and_contacts.md](./newton/runtime_and_contacts.md)
3. Read [phystwin/artifacts.md](./phystwin/artifacts.md)

## Scope Boundary

This workspace has a hard rule:

- `Newton/newton/` is read-only for project work.

So this encyclopedia documents Newton core by source analysis, but project-side
changes should happen in `Newton/phystwin_bridge/` or other bridge/report code.

## Current Priority

The bridge layer is the fastest-moving part of the project, so documentation
effort should begin there. PhysTwin and Newton sections should explain the
stable foundations; bridge pages should explain the current research workflow.
