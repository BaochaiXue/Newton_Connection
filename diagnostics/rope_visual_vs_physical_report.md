# Rope Visual Vs Physical Report

- c12 render/physical radius ratio: `0.999908`
- c08 visible-tool control keeps render and physical rope radius aligned at 1.0x.

## Interpretation

The honest path is to keep rope render thickness aligned with physical contact thickness. Sphere inflation should not be used to compensate for a rope-thickness lie.
