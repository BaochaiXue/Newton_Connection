> status: active
> canonical_replacement: none
> owner_surface: `video_presentation_quality`
> last_reviewed: `2026-04-01`
> review_interval: `21d`
> update_rule: `Update when visual QA gates, skeptical-review policy, or video acceptance criteria change.`
> notes: Active canonical task page for meeting-facing video readability and acceptance quality.

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

## Delivery Contract

- publish/result GIFs:
  - stored next to the promoted result artifacts
  - intended for sharing/release quality
  - each single GIF must stay below `40 MB`
- deck/PPTX GIFs:
  - stored under the meeting slide `gif/` directory
  - may be compressed relative to the publish GIFs so the final `pptx`
    remains below `100 MB`
  - deck compression must not overwrite the publish/result GIFs

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
