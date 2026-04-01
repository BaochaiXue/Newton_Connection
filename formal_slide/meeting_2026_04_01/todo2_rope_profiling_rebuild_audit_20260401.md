# TODO 2 Rope Profiling Rebuild Audit — 2026-04-01

## Scope

Audit target:

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`
- `formal_slide/meeting_2026_04_01/transcript.md`

Section under review:

- TODO 2 / rope-case profiling section only

## What Was Already Good

- The high-level research order was already mostly correct:
  - fair benchmark
  - source evidence
  - throughput result
  - gap interpretation
  - optimization implication
- The section was already rope-case only at the conclusion level.
- The section already separated throughput evidence from attribution evidence.

## Main Problems Found Before Rebuild

1. Slide 8 did not visually establish fairness strongly enough.
   - It used a GIF plus bullets.
   - It did not use a compact fairness table, so the controls were harder to scan in 15 seconds.

2. Slide 9 had asymmetric physical-intent evidence.
   - Newton side used a generic particle integration kernel.
   - PhysTwin side used a more rope-specific spring/dashpot force block.
   - This made the Newton proof look weaker than the PhysTwin proof.

3. Slide 11 mixed a valid core claim with a wrapper-dependent call-chain explanation.
   - The core code excerpt itself was acceptable.
   - But the transcript leaned on our rope viewer entry to argue that this was the relevant Newton path.
   - That use is acceptable only as methodology context, not as the main proof of core behavior.

4. Slide 12 was too conclusion-shaped and not evidence-shaped enough.
   - It used body bullets instead of a compact evidence table.
   - It did not explicitly separate bridge tax from the residual post-bridge cost on the slide face.

5. Unused profiling chart helpers still existed in the build script.
   - They were not the current slide content.
   - But they still violated the new rule against plots/charts/self-drawn figures in this section.

6. The transcript was detailed, but some claims were still stronger than the source evidence.
   - “runtime structure / launch structure” was directionally supported.
   - But the old wording could still be read as stronger causality than the code alone justified.

## Weak Citations / Evidence Mismatch

### Wrapper-leaning evidence

- The profiling section still mentioned the rope viewer entry path to connect the benchmark to `SolverSemiImplicit`.
- That is valid as a methodology note only.
- It is not strong enough as the main proof of Newton core execution structure.

### Asymmetric proof strength

- Old Newton P1 evidence:
  - generic semi-implicit particle update
- Old PhysTwin P1 evidence:
  - rope-specific spring + dashpot + force-to-velocity update

This mismatch made the “same physics intent” claim feel stronger on the PhysTwin side than on the Newton side.

### Over-strong claim boundary

- “The slow path is runtime structure, not rope physics” was too strong as a slide title for the available evidence.
- A more honest boundary is:
  - the residual gap looks more consistent with execution / launch structure than collision
  - bridge tax is real, but not the whole gap

## Which Slides Needed GIF Support

- Benchmark method slide: yes
- Throughput result slide: yes
- Bottleneck / bridge-tax slide: yes
- Source-only code slides: GIF optional

## Which Slides Had Too Much Text

- Slide 8: too much fairness information in bullets rather than a table
- Slide 11: too much explanation burden in transcript because the slide itself did not expose the bridge-vs-residual split compactly

## Which Transcript Sections Failed The Intended 1:50 Standard

Not catastrophic, but two improvements were needed:

- Newton physical-intent transcript needed a more rope-specific core explanation instead of relying on a generic integrator kernel
- Runtime-structure transcript needed a clearer What / Why / Risk separation so the launch-structure claim stayed honest

## Stronger Evidence Sources Chosen For The Rebuild

### Newton core files

- `Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py`
  - rope spring-damper force assembly
- `Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py`
  - decomposed semi-implicit multi-stage step organization

### PhysTwin core files

- `PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py`
  - rope spring + dashpot force update
  - force-to-velocity update
  - graph capture / `forward_graph`

### Wrapper/harness evidence retained only as methodology

- `Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py`
  - used only to describe the fairness setup and the benchmark entry path
  - no longer used as the main proof of Newton core runtime behavior

## Slide-by-Slide Rebuild Plan

1. Slide 8
   - replace bullets with a compact fairness table
   - keep one rope GIF
   - make it explicitly a method slide

2. Slide 9
   - replace the generic Newton integrator excerpt with a rope-specific Newton spring kernel excerpt
   - keep PhysTwin rope spring/dashpot excerpt
   - lower claim strength to “comparable spring-damper rope update intent”

3. Slide 10
   - keep it as the main throughput table slide
   - keep one rope GIF
   - move metadata to note/transcript

4. Slide 11
   - rebuild as a compact bridge-tax-vs-residual evidence table
   - keep one rope GIF
   - avoid overclaiming collision causality

5. Slide 12
   - keep it as the runtime-interpretation / optimization-implication slide
   - main evidence becomes:
     - Newton core multi-stage step organization
     - PhysTwin core graph capture
     - compact Nsight summary in the slide note
   - conclusion lowered to:
     - residual gap looks more like launch structure than collision

## Rebuild Outcome Target

After rebuild, the profiling section should satisfy:

- rope-case only
- fair benchmark first
- gap second
- bridge tax vs residual third
- launch-structure interpretation last
- core claims supported by Newton core + PhysTwin core
- wrapper only as methodology
- no plots/charts/self-drawn diagrams
