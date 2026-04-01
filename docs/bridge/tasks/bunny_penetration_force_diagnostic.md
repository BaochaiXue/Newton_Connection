# Task: Bunny Penetration Mechanism Diagnostic

## Objective

Turn bunny penetration from a vague symptom into an evidence-backed mechanism
claim. This task is complete only when the team can defend, with matching
videos + summaries, whether the failure is:

- a generic rigid-contact failure
- a direction / effective-normal problem
- an insufficient-contact-magnitude problem
- an internal-force / inertia dominance problem
- or a geometry- and momentum-sensitive mixture

## Main Script

- `Newton/phystwin_bridge/demos/demo_cloth_bunny_drop_without_self_contact.py`

## Scope

This task is strictly for the OFF-only cloth vs rigid mechanism study.

Included:

- one deformable cloth
- one rigid target (`bunny` or `box`)
- optional ground
- trigger-substep force diagnostics
- parity check
- short diagnostic videos / snapshots

Explicitly excluded:

- self-collision transfer or resolution
- Newton core kernel rewrites
- rope / MPM / robot-side transfer
- claiming that radius or brute-force parameter sweeps are the main result

## Required Deliverables

### 1. Physics Deliverables

Each required case must produce:

- `force_diag_trigger_substep.npz`
- `force_diag_trigger_summary.json`
- `force_diag_trigger_snapshot.png`
- `force_diag_trigger_snapshot.mp4`
- rollout `summary.json`

### 2. Diagnostic Deliverables

Each summary must support reading:

- `wrong_direction_ratio`
- `inward_acceleration_ratio`
- `geom_contact_without_force_ratio`
- `internal_dominates_ratio`
- `median_ext_over_stop`
- `median_penetration_mm`
- `dominant_issue_guess`

### 3. Visualization Deliverables

The task is not done just because artifacts exist. The artifacts must be
meeting-readable.

Required visualization outputs:

- a short force-diagnostic clip
- a close-up snapshot
- at least one full-rollout support / sanity video
- a 4-case comparison board or slide
- when requested for contact-mechanism review:
  - a self-collision-OFF `2 x 2` board video covering:
    - `box + cloth` penalty force on every cloth node colliding with the box
    - `box + cloth` total force on the same contact-node set
    - `bunny + cloth` penalty force on every cloth node colliding with the bunny
    - `bunny + cloth` total force on the same contact-node set
  - each panel must run from rollout start through `1.0 s` after first rigid contact
  - node selection must be framewise and exhaustive over the rigid-contact set,
    not top-k only

## Required Experiment Matrix

The minimum experiment set is four cases:

1. `bunny_baseline`
2. `box_control`
3. `bunny_low_inertia`
4. `bunny_larger_scale`

Appendix-only sweeps:

- particle radius
- damping / stiffness sweeps
- dt / substeps sweeps

## Acceptance Criteria

### A. Physics KPI

- The 4-case matrix is complete.
- The rigid support does not visibly collapse under the chosen diagnostic
  workpoint.
- The final claim is not a black-box “looks bad” statement.

### B. Diagnostic KPI

- Trigger-substep snapshot is captured for every case.
- Geometry contact and force contact are reported separately.
- Force direction and force magnitude can both be argued from the outputs.
- Parity check is available and bounded enough to be practically usable.

### C. Visualization KPI

- The main subject is large enough to read without zooming into a screenshot.
- The contact ROI is clearly visible.
- The force clip shows the normal plus force families clearly enough to support
  a mechanism claim.
- A viewer can tell the difference between the bunny baseline and the box
  control without reading code.
- The video itself, not only the JSON, supports the verbal conclusion.

#### C1. Composition KPI

- `SOR` = subject occupancy ratio
  - main video target: `0.20 ~ 0.45`
  - force video target: `0.18 ~ 0.40`
- `CRR` = contact ROI ratio
  - force video main panel target: `>= 0.10`
- `EBR` = empty background ratio
  - main video target: `<= 0.50`
  - force video target: `<= 0.35`
- `TOR` = text overlay ratio
  - main video target: `<= 0.06`
  - force video target: `<= 0.08`

#### C2. Time Coverage KPI

- `PCS` = phase coverage score
  - main video target: `5 / 5`
  - required phases:
    - pre-contact
    - trigger
    - growth
    - max penetration
    - rebound / settle trend
- `TAE` = trigger alignment error
  - ideal: `0`
  - acceptable: `<= 1 substep`

#### C3. Force Glyph KPI

- top-k in main force video: `6 ~ 8`
- appendix top-k: `<= 10`
- `APL` = arrow pixel length range
  - readable target: `20 px ~ 80 px`
  - `< 15 px` is considered unreadable
- `AOR` = arrow overlap rate
  - main force video target: `<= 0.25`
- anchor correctness is mandatory:
  - white normal must anchor to contact / closest point
  - gray closest-to-particle must be visible
  - red / purple / green must explain the same local contact patch

#### C4. Semantic Consistency KPI

- fixed colors across every case:
  - white = outward normal
  - gray = closest-to-particle
  - red = external normal
  - purple = internal normal
  - green = acceleration normal
- camera must stay consistent across:
  - bunny baseline
  - box control
  - bunny low inertia
  - bunny larger scale

#### C5. Magnitude Observability KPI

Because force arrows are normalized per family, the force video must also carry
numbers or a HUD. At minimum the force view must expose:

- max penetration mm
- geom-contact node count
- force-contact node count
- median external normal
- median internal normal
- median acceleration normal
- median ext/stop
- internal_dominates_ratio
- wrong_direction_ratio

## Current Evidence (2026-03-30)

Current canonical matrix result bundle:

- `results/bunny_force_visualization/runs/20260331_025500_fullprocess_force_matrix_v3`
- `results/bunny_force_visualization/runs/20260331_025500_fullprocess_force_matrix_v3/summary.json`
- `results/bunny_force_visualization/runs/20260331_025500_fullprocess_force_matrix_v3/artifacts/matrix/bunny_penetration_summary_board.png`

Current fixed workpoint used for matrix:

- cloth total mass = `0.1 kg`
- rigid mass = `0.5 kg`
- `normal_only`
- `trigger + 8 substeps`

Current evidence-backed conclusion:

- Not a wrong-direction failure:
  - all four matrix cases currently report `wrong_direction_ratio = 0.0`
- Not a generic rigid-contact failure:
  - `box_control` shows a broad support patch (`2116` contact nodes),
    while `bunny_baseline` shows only `2`
- Momentum-sensitive:
  - reducing impact speed improves penetration severity
- Best current diagnosis:
  - the bunny case is a sparse early-contact case with insufficient effective
    contact magnitude on the local support patch

## Current Status

### Current Closure State

- Physics diagnostic tooling exists.
- The task is now closed under the stricter full-process meeting criteria.
- The accepted canonical run is:
  - `results/bunny_force_visualization/runs/20260331_231500_fullprocess_sync_matrix_manual_v2`
- The accepted rendering path is:
  - phenomenon video rendered once as the stable global truth
  - force mechanism video composed over that phenomenon render
  - projected 2D force overlays + zoom panel
  - no trigger-only montage as the final meeting artifact
  - exact active-interval force synchronization with per-frame mapping reports
- The accepted 4-case package now includes:
  - `bunny_baseline`
  - `box_control`
  - `bunny_low_inertia`
  - `bunny_larger_scale`
- All four cases now have:
  - phenomenon video
  - full-process force mechanism video
  - contact sheets
  - QA report / verdict
  - case README
- Latest pointers and result index now point at the accepted `v3` run.
- Every accepted force video now has:
  - `force_diag_trigger_window_mapping.json`
  - `exact_mapping_ratio_active_interval = 1.0`
  - `reused_mapping_ratio_active_interval = 0.0`
- A new requested add-on workflow is now in progress for mechanism review:
  - self-collision remains OFF
  - box control and bunny baseline stay on the standard support setup so the
    rigid target remains physically stable during the clip
  - a new board render path is being added to visualize all rigid-contact cloth
    nodes per displayed frame instead of only top-k probes

## Definition Of Done

This task is done only when:

1. the 4-case matrix is complete,
2. every case has a trigger-aligned diagnostic artifact set,
3. the comparison board / slide is built,
4. the main process video satisfies `PCS = 5/5`,
5. the force video satisfies the visualization KPI above,
6. the final claim is:
   evidence-backed, bounded, and visually defensible.
