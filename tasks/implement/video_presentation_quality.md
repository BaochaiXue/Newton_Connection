# Implement: video_presentation_quality

## Preconditions

- inspect the promoted video bundles and current validators
- identify whether the problem is framing, contrast, timing, or scene reference

## Canonical Commands

```bash
rg --files Newton/phystwin_bridge/demos | rg 'demo_'
rg --files scripts | rg 'validate.*video|render_gif'
```

## Step Sequence

1. inspect the current promoted videos and their QA outputs
2. choose whether to improve, replace, or retire each weak video
3. update render defaults and rerun validation when a video remains in scope

## Validation

- skeptical video review artifacts exist for promoted videos
- camera and process visibility support the claim

## Output Paths

- promoted demo result bundles
- slide/media assets that depend on them
