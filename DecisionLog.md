# Decision Log

## 2026-03-30

### D-0001

- Decision: treat `Newton/phystwin_bridge/demos/demo_robot_rope_franka.py` as
  the authoritative final-path candidate for the native robot + deformable demo.
- Reason: it is the only current native Newton robot asset path in the local
  repo and stays on the semi-implicit bridge pipeline.

### D-0002

- Decision: treat `demo_rope_control_realtime_viewer.py` as a profiling/support
  path, not a final demo path.
- Reason: it is useful for runtime analysis but not a taskful final presentation
  demo.

### D-0003

- Decision: canonical robot demo outputs must be promoted under
  `results/robot_deformable_demo/` rather than left only in `tmp/`.
- Reason: later agents need a single authoritative place to look.

### D-0004

- Decision: the mission mention of `demo_robot_rope.py` is treated as a legacy
  reference, because that script is not present in the current local repo.
- Reason: only `demo_robot_rope_franka.py` and legacy `tmp/demo_robot_rope_*`
  artifacts exist locally.

### D-0005

- Decision: the authoritative best native robot + deformable run is
  `results/robot_deformable_demo/runs/20260330_213045_native_franka_lift_release_presentation`.
- Reason: this run stays on the semi-implicit native Franka path, passes the
  automatic video gates, has explicit recorded manual multimodal review, and
  has final contact metrics aligned with the visible interaction.

### D-0006

- Decision: robot/deformable contact for the final summary is measured with the
  calibrated `finger-span` proxy family:
  `min(gripper_center, left_finger, right_finger, finger_span)`.
- Reason: the old gripper-center-only metric missed visible contact; the
  calibrated proxy used for the authoritative run yields a defensible
  first-contact / contact-duration story that matches the actual video.

### D-0007

- Decision: archive the earlier canonical attempts under `results/.../rejected/`
  instead of deleting them or leaving them in `runs/`.
- Reason: future agents need a clean authoritative best run, but they also need
  preserved evidence for why the earlier servo regression and pre-summary-fix
  attempt were rejected.

### D-0008

- Decision: keep `20260330_213045_native_franka_lift_release_presentation` as
  the authoritative best run even after the later replay-controller experiments.
- Reason: `213045` already satisfies the full validation contract under the
  simplest default command path and is easier to defend as the repo's primary
  reproducible meeting asset than the later archived replay-controller variants.

### D-0009

- Decision: regenerate the March 25 meeting deck and transcript against the
  authoritative robot run.
- Reason: the builder had drifted to a rejected run id; regenerating the deck
  re-synchronized the presentation layer with the validated `213045` bundle.

### D-0010

- Decision: treat the native robot rope drop/release sanity baseline as a
  separate milestone with its own result bundle and task scaffold.
- Reason: the old lift-release robot run is useful history, but it should not
  be overloaded with the narrower stage-0 release/drop evidence or confused
  with a final two-way-coupling claim.

### D-0011

- Decision: promote
  `results/native_robot_rope_drop_release/runs/20260331_040614_native_franka_drag_off_w5_readable`
  as the provisional stage-0 native robot release/drop baseline.
- Reason: both drag OFF and drag ON stayed gravity-like in the matched 5 kg
  A/B comparison, so drag was not the main cause of non-gravity-like fall; the
  drag-OFF run is easier to defend visually because the pre-release
  support/release sequence reads more clearly while the full video and physics
  QA still pass.

### D-0012

- Decision: keep the recoil-free release/drop baseline as the actual
  acceptance target for this milestone.
- Reason: the current provisional promoted run still shows release
  recoil/catapulting, so the bundle should be treated as ready to supersede
  rather than final.

### D-0013

- Decision: promote
  `results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5`
  as the authoritative stage-0 native robot release/drop baseline.
- Reason: this run keeps the visible holder aligned with the constrained patch,
  passes the pre-release settle gate, keeps the post-release horizontal kick
  below the hard threshold, preserves gravity-like early fall, lands on a real
  ground, and passes the full video QA bundle. The matched drag-ON recoil-fixed
  run also passes, and the A/B comparison now indicates only a minor drag
  effect.
