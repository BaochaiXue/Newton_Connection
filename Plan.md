# Plan

## Goal

Keep the native Franka rope path authoritative, reproducible, and presentation-ready.

## Completed Milestones

1. Audit current code path and legacy outputs
2. Normalize results hierarchy under `results/robot_deformable_demo/`
3. Build a strict video validation pipeline with ffprobe, contact sheets, event sheets, and verdicts
4. Repair the robot/deformable contact summary so the metrics match the visible finger-span interaction
5. Produce and promote an authoritative best run
6. Update meeting slide/material references to the canonical result

## Maintenance Rule

If a later agent changes the native Franka demo behavior, it must:

1. create a new canonical run under `results/robot_deformable_demo/runs/`
2. regenerate validation artifacts
3. compare against `BEST_RUN.md`
4. update slide/material references if the best run changes

## Current Focus

- no open execution milestone in this task
- maintain the current authoritative run unless a better validated native Franka result supersedes it
