# Handoff: robot_table_rope_split_mujoco_semiimplicit

## Current Milestone

Milestone 1: truthful one-way direct-finger split demo.

## What Changed

- task/spec/plan/status surfaces were created
- the split demo and wrapper now exist:
  - `Newton/phystwin_bridge/demos/demo_robot_table_rope_split_mujoco_semiimplicit.py`
  - `scripts/run_robot_table_rope_split_demo.sh`
- the best-known one-way artifact is:
  - `/tmp/robot_table_rope_split_one_way_fine_v5`
- a real two-way bookkeeping bug was fixed:
  - rope reaction wrench is now read from the post-step rope state instead of
    the force-cleared pre-step state

## Current Conclusion

The split architecture is now implemented and runs end-to-end. The current
best-known one-way result proves:

- truthful physical-only rope rendering
- simultaneous rope-ground and rope-table support contact
- stable robot path without scraping the table

But the current motion layout still misses `finger first contact`, so milestone
1 is not yet accepted. Two-way robot-rope reaction remains milestone 2.

## Exact Next Command

```bash
bash scripts/run_robot_table_rope_split_demo.sh /tmp/robot_table_rope_split_one_way_fine_v5 --num-frames 120 --coupling-mode one_way
```

## Current Blocker

The blocker is no longer solver instability. The blocker is geometric:

- the current table-edge drape is stable
- the finger path no longer scrapes the table in the best-known run
- but the leading finger still does not intersect the settled tabletop rope
  segment early enough to register first contact

## Last Failed Acceptance Criterion

- `first_finger_rope_contact_frame` is still `null` in the best-known one-way
  fine-step artifact

## Key GIF / Artifact Paths

- `/tmp/robot_table_rope_split_one_way_fine_v5/summary.json`
- `/tmp/robot_table_rope_split_one_way_fine_v5/hero.mp4`
- `/tmp/robot_table_rope_split_one_way_fine_v5/contact_sheet.jpg`

## What Not To Redo

- do not rebuild this on the retired local robot controller stack
- do not widen rope render thickness for readability
- do not make two-way a hidden prerequisite for first acceptance
- do not go back to coarse rope stepping; the `64`-substep one-way runs were not
  stable enough to trust

## Missing Evidence

- a one-way artifact with non-null `first_finger_rope_contact_frame`
- a first-contact window where the leading pad is the purposeful contactor
- a two-way artifact with nonzero rope-to-robot wrench after contact

## Context Reset Recommendation

- recommended: yes
- reason:
  - the task chain now contains the implementation boundary; future agents
    should be able to continue without chat memory
