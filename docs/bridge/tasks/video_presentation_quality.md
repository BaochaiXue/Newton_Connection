# Task: Video Presentation Quality

## Question

How do we make all demo videos function as evidence rather than decorative media?

## Why It Matters

Meeting feedback shows the issue is not only physics quality but presentation
readability:

- contact region too small
- insufficient spatial reference
- weak viewpoint choice
- ground/support not visually clear

## Main Levers

- better viewpoint
- visible ground/reference geometry
- closer crop on contact region
- same-camera comparisons for A/B videos
- higher presentation quality GIF generation

## Code Entry Points

- offline render functions in `Newton/phystwin_bridge/demos/*.py`
- GIF generation helpers in slide builders / demo scripts

## Current Default

Most renderers now use an earth-tone ground palette through shared bridge-side
helpers.

## Success Criteria

- viewer can understand the physical point in 5-10 seconds
- contact/support/penetration is visually obvious
- comparison videos are aligned and fair

## Open Questions

- Which current videos still need re-recording with better camera placement?
- Which demos should be deleted instead of polished?
