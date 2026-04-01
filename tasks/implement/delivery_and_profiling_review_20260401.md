# Implement: delivery_and_profiling_review_20260401

## Preconditions

- Read `AGENTS.md`, `docs/README.md`, `TODO.md`
- Read the review task page and linked task pages
- Confirm current dirty files so the audit does not overwrite active work

## Canonical Commands

```bash
sed -n '1,260p' formal_slide/meeting_2026_04_01/build_meeting_20260401.py
sed -n '1,260p' formal_slide/meeting_2026_04_01/transcript.md
find results/native_robot_rope_drop_release -maxdepth 3 -type f
find results/rope_perf_apples_to_apples -maxdepth 4 -type f
```

## Step Sequence

1. Extract slide and transcript claims, then compare them against task pages and result summaries
2. Inspect promoted demo outputs, QA sheets, and validation JSON for visibility and physics risks
3. Review profiling artifacts and decide whether the current plan misses bridge, batching, collision, or instrumentation blind spots

## Validation

- cite files for each conclusion
- avoid conclusions that contradict current promoted artifacts

## Output Paths

- `formal_slide/meeting_2026_04_01/`
- `results/native_robot_rope_drop_release/`
- `results/rope_perf_apples_to_apples/`
