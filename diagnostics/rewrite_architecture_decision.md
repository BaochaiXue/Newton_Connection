# Rewrite Architecture Decision

Date: 2026-04-08

## Candidate set

### Candidate A

Single-solver `SolverSemiImplicit` rewrite with direct finger, online reference
generation, and physically actuated execution.

### Candidate B

`SolverSemiImplicit` deformable path + native Newton IK-style online reference +
`joint_target_pos` execution, still direct finger, no precomputed truth path.

### Candidate C

Split architecture inspired by official native Newton demos:

- robot + table use a robot-first articulated pattern
- rope remains on a deformable solver path
- coupling stays geometry-honest
- direct finger remains the visible/physical contactor

## Ranking criteria

- consistency with official Newton demos
- consistency with physics
- likelihood of satisfying:
  - stable startup
  - real table blocking
  - readable rope push
- amount of custom machinery
- geometry truth
- multimodal visual honesty

## Evaluation

### Candidate A

Pros:

- least architectural change
- stays closest to the current bridge rope path

Cons:

- official Newton examples do not present this as the strongest articulated
  robot pattern
- our rewrite experiments still sag during `pre` even after:
  - removing overwrite
  - fixing EE reference offset
  - using reachable seeded waypoints
  - increasing gains
  - increasing armature

Verdict:

- physically honest, but currently weak on startup stability

### Candidate B

Pros:

- much better than the old giant demo
- adopts the correct native-style control shape:
  - online IK
  - `joint_target_pos`
  - solver-owned body truth

Cons:

- still relies on the same articulated actuation surface and solver route that
  is currently sagging in `pre`
- our v2 rewrite already tested this family honestly and still failed:
  - `smoke_v4`
  - `highgain_v2`
  - `armatureprobe`

Verdict:

- the correct bridge-side rewrite shape for diagnosis
- not enough by itself to satisfy all three final requirements

### Candidate C

Pros:

- best match to official Newton robot + deformable examples
- respects solver specialization
- gives the robot side a more native articulated control path
- leaves the rope on the deformable side where SemiImplicit/VBD-style handling
  is already natural

Cons:

- larger rewrite
- coupling work must be done carefully to stay geometry-honest

Verdict:

- highest likelihood of satisfying all three requirements together

## Decision

**Choose Candidate C as the target final architecture.**

Reason:

The rewrite evidence already shows that Candidate B is a valid diagnostic
rewrite but still fails on the same startup-sag mechanism.
That is strong evidence that continuing to iterate inside the same
bridge-side articulated actuation surface is unlikely to produce the final pass
without disproportionate custom machinery.

## Practical implication

The new v2 rewrite is not wasted work.

It established:

- the old overwrite path is gone
- the real blocker is now isolated
- the honest next move is solver/architecture escalation, not another cosmetic
  patch

So the rewrite path becomes:

1. keep v2 as the clean bridge-side diagnostic baseline
2. use it as the control-plane reference for a split-architecture experiment
3. evaluate whether the robot side must move to the more official articulated
   robot-first pattern while the rope remains on the deformable path
