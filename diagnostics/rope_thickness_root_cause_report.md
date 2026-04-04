# Rope Thickness Root-Cause Report

- promoted c12 rope physical radius: `0.026002 m`
- promoted c12 rope render radius: `0.026000 m`
- promoted c08 visible-tool rope physical radius: see rope_visual_vs_physical_thickness_report.md

## Interpretation

The old accepted c12 baseline used a physically much thicker rope than the later true-size branches. That reduced geometric precision demands and made stale contact geometry easier to overlook.
This is a real secondary contributor: once the rope becomes physically smaller, the same reference/path mismatch is no longer hidden by the rope thickness.
But it is not the primary cause, because c19 shows the thin rope can still be hit early when laydown and base alignment are corrected.
