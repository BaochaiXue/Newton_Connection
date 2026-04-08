# Split V3 Final Causal Account

Date: 2026-04-08

## Current causal conclusion

The v2 rewrite eliminated the easy causes but did not eliminate startup sag.

That means the remaining blocker is not:

- FK overwrite
- render mismatch
- hidden support prop
- unreachable rough Cartesian targets alone

It is the articulated execution route itself.

## Physics interpretation

If a robot cannot hold its intended pre-contact pose under gravity with solver
executed motion, then the table becomes the first structure that carries the
load. That visually reads as collapse/resting, not purposeful interaction.

Because the table loading happens before intended contact, readable finger-to-
rope push never becomes the dominant visible event.

## Architectural implication

The robot side needs to move onto a more native robot-first pattern, while the
rope remains on the deformable path.

That is the split-v3 workstream.
