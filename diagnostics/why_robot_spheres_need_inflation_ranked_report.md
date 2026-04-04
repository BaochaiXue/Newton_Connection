# Why Robot Spheres Need Inflation Ranked Report

## Ranked Hypotheses

1. H1 wrong contact reference point
2. H3 XY trajectory / laydown miss
3. H4 rope physical thickness smaller than old mental model
4. H2 stale Z stack as a secondary contributor
5. H5 proxy semantics misleading as a diagnostics-layer contributor
6. H6 controller semantics as a secondary, non-primary contributor for this specific question
7. H7 combination

## Primary Root Cause

H1 wrong contact reference point combined with H3 XY / laydown miss

## Secondary Contributors

- H4 rope physical thickness became much smaller in true-size runs
- H2 stale vertical geometry assumptions survive in the mental model, but the current joint_trajectory path is not primarily driven by the tabletop Z clearance args
- H5 proxy semantics can make a near-miss look solved earlier, but are not the accepted proof surface in c12
- H6 controller semantics matter for blocked-physics claims, but are secondary for explaining why larger proxy spheres seemed necessary in the readable tabletop rope case

## Key Evidence

- In promoted c12, the command target is effectively gripper-center based, while the mean target -> nearest finger-box surface distance is `0.042400 m`.
- The accepted proxy effective radius in c12 is `0.033000 m`, which is the same order as that reference-to-surface gap.
- At first actual contact in c12, gripper-center -> actual contact surface distance is `0.078049 m`.
- True-size rope contact timing changes from `4.335500 s` in c15 to `1.233950 s` in c19 without changing ee-contact-radius, which points to laydown/base/path alignment rather than sphere size.
- The visible-tool control c08 reaches first actual tool contact at `1.734200 s` with `multi_frame_standoff_detected = false`, proving the same rope/tabletop context can be hit honestly without sphere fiction when the contactor is explicit.

## What Sphere Inflation Was Actually Compensating For

The inflated sphere was mainly compensating for the fact that the tabletop command reference lived at gripper-center, while the real contact-capable surface lived several centimeters away on the finger boxes. Once the rope became physically thinner, stale laydown/base alignment made that mismatch show up as an XY near-miss. The larger sphere did not make the finger more physical; it simply enlarged a proxy centered on the wrong point so that the proxy could still 'catch' the rope.

## Is Sphere Inflation Physically Meaningful?

- For the current rope tabletop path: `No`.
- It is a proxy workaround, not a real physical need.

## Honest Path Forward

- direct-finger re-certification is only honest if the reference geometry and laydown/path are corrected so actual finger boxes reach the rope without sphere fiction;
- the promoted visible rigid tool baseline is the current conservative control for a meeting-safe honest contactor;
- physical-blocking remains a separate blocked follow-on task and is not solved by sphere inflation.

## Meeting-Ready Conclusion

The inflated robot spheres were mostly compensating for an abstract gripper-center reference and stale scene/path alignment, not for any fundamental rope-physics need.

## Engineering Conclusion

In the direct-finger tabletop path, the commanded reference follows the FK gripper center, while the real contact-capable geometry is several centimeters away on the finger boxes. When laydown/base alignment is stale, that gap becomes a real XY near-miss; enlarging a sphere centered on gripper-center simply papers over the mismatch.

## Research Conclusion

Sphere inflation is best understood as a proxy workaround for contact-geometry mismatch. An explicit honest contactor, as shown by the promoted visible-tool baseline, can hit the same rope/tabletop context without any sphere fiction, which means inflation should not be treated as physically necessary.
