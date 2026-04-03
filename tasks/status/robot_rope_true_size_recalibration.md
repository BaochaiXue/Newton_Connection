# Status: robot_rope_true_size_recalibration

## Current State

- Active
- Goal is to recover a natural laydown and visible true finger contact after
  shrinking the rope's physical radius

## Last Completed Step

- Re-read the current tabletop hero control plane and started bounded
  physical-radius sweep candidates.

## Next Step

- Finish the initial sweep set and compare `1.0x`, `0.25x`, and `0.1x`
  physical-radius videos before changing coupled laydown/contact parameters.

## Blocking Issues

- None yet; diagnosis and sweep generation are in progress.

## Artifact Paths

- current accepted baseline:
  - `Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/`
- true-size candidates:
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260402_140811_physradius0p1_c15/`
  - `Newton/phystwin_bridge/results/robot_rope_franka/candidates/20260403_000517_physradius0p25_c16/`
- diagnosis board:
  - `diagnostics/robot_rope_true_size_recalibration_board.md`
