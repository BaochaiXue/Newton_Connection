# Finger Vs Proxy Geometry Report

- actual robot contactor in the direct-finger path: `URDF finger BOX colliders`, not spheres
- accepted c12 proxy effective radius: `0.033000 m`
- accepted c12 mean target -> nearest finger-box surface distance: `0.042400 m`
- accepted c12 first-contact gripper-center -> actual contact surface distance: `0.078049 m`

## What The Sweep Shows

The current code never inflates the actual finger collision boxes. Sphere inflation only appears in proxy-clearance semantics centered on gripper-center / left-finger / right-finger / finger-span.

In c12, the nominal proxy radius is already close to the command-reference-to-finger-surface gap. That means a bigger sphere is mainly compensating for the fact that the reference point is not on the real contact-capable finger surface.

Because the proxy sweep is computed on the same saved rollout history, any onset shift from changing sphere size is purely a proxy/measurement effect, not a physical-scene effect.
