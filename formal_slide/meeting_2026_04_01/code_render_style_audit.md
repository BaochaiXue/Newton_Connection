# Code Render Style Audit — 2026-04-01

## Scope

Updated the slide-generation source so code snippets are rendered as synthetic
editor panels instead of light-theme code screenshots.

Primary source of truth:

- `formal_slide/meeting_2026_04_01/build_meeting_20260401.py`

Primary affected slides:

- `Slide 9` — `Source Proof P1: Same Replay, Different Execution Style`
- `Slide 14` — penetration-analysis source-proof code slide

## What The Old Render Looked Like

- light background panel
- plain rounded rectangle with minimal framing
- low-contrast syntax coloring
- bright yellow underline/highlighter bars
- small code panels that still felt like screenshots instead of source proof

The result was programmatic, but it did not read visually like a modern editor
capture and it did not hold attention well at slide scale.

## What Changed

- replaced the old light code-block renderer with a VSCode-like synthetic dark editor panel
- added a dark editor background and darker title bar
- added subtle editor chrome with a file-title strip and muted path label
- added a real gutter region for line numbers
- replaced yellow highlighter bars with soft line-level blue emphasis strips
- increased code font size and panel export size
- added line truncation with `...` instead of silent hard clipping
- enlarged the `Source Proof` slide layout so code occupies more of the page
- routed `code_twocol` slides through the same larger code-panel layout

## VSCode-Like Theme Rules

- editor background: `#1E1E1E`
- chrome / gutter background: `#252526`
- default text: `#D4D4D4`
- path label: `#9CDCFE`
- keywords: `#569CD6`
- strings: `#CE9178`
- comments: `#6A9955`
- function names: `#DCDCAA`
- builtins / classes: `#4EC9B0`
- numbers: `#B5CEA8`
- highlight strip: `#264F78`
- highlight accent: `#3794FF`

## Font Policy

Preferred monospace fallback order in the builder:

1. Cascadia Code / Cascadia Mono
2. JetBrains Mono
3. Consolas
4. Noto Sans Mono
5. DejaVu Sans Mono
6. Liberation Mono

Font fallback was needed on this host.
Detected practical renderer fallback:

- `NotoSansMono-Regular.ttf`
- `NotoSansMono-Bold.ttf`

## Layout Rules

- excerpt length stays `<= 20` rendered lines
- highlighted lines stay `<= 5`
- code panels export at larger pixel dimensions before PPTX placement
- the performance `Source Proof` slide now prioritizes readable code over empty whitespace
- slide text remains short; detailed interpretation still belongs in `transcript.md`

## Result

The regenerated code panels are now visibly closer to VSCode Dark+:

- dark editor feel
- crisp monospace rendering
- clearer syntax color separation
- readable highlighted lines
- more credible source-proof presence at slide scale

This is still a synthetic render, not a GUI screenshot, which keeps the build
pipeline reproducible and reusable for future slides.
