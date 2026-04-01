# Documentation Style Guide

This encyclopedia should stay structured as the codebase evolves.

## Page Template

Most technical pages should follow this order:

1. Purpose
2. Why this matters to the project
3. Key concepts
4. Code entry points
5. Data / runtime contracts
6. Current implementation status
7. Known gaps / open questions
8. Related pages

## Writing Rules

- Prefer stable concepts over transient experiment chatter.
- Use file paths whenever a behavior is implemented in code.
- Distinguish clearly between:
  - confirmed behavior
  - current hypothesis
  - open question
- If a page summarizes an experiment pattern, state the exact script(s) and outputs involved.
- If a page depends on an upstream repo assumption, say so explicitly.

## Terminology Rules

- Use `PhysTwin`, `Newton`, and `bridge` consistently as separate layers.
- Use `IR` only after defining which IR variant you mean.
- When saying `contact`, specify whether it is:
  - particle-particle
  - particle-shape
  - rigid-rigid
  - self-collision
- When saying `viewer` or `render`, specify whether it is:
  - offline MP4 rendering
  - interactive viewer
  - diagnostic snapshot rendering

## Evidence Rules

For research-facing pages, do not collapse everything into conclusions.
Always separate:

- what the code does
- what the experiment output says
- what interpretation we currently favor

## Maintenance Rules

- Update existing pages before creating duplicate pages.
- Prefer adding a short `Open Questions` section instead of scattering TODOs.
- If a topic grows large, split by concept, not by date.
