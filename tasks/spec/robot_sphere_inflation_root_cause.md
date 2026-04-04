# Spec: robot_sphere_inflation_root_cause

## Goal

Identify, rank, and defend the real mechanism behind why inflated robot
spheres/proxies appeared necessary in the tabletop rope case.

## Scope

- Bridge/demo layer only
- No edits under `Newton/newton/`
- Use current accepted tabletop baseline, current visible-tool baseline, and
  current blocked physical-blocking diagnostics as evidence/control surfaces

## Must Answer

1. What exact code paths use sphere/proxy semantics?
2. Which of the candidate hypotheses H1-H7 is primary?
3. What secondary contributors matter?
4. Is sphere inflation physically meaningful or a workaround?
5. Should it be removed, reduced, replaced, or kept only as a diagnostic aid?

## Required Evidence

- code audit over all sphere/proxy/contact-radius surfaces
- measured geometry offsets and reachability
- bounded disambiguating experiments
- full-video review where the claim depends on visible contact timing

## Constraints

- no hidden helper
- no fake geometry explanation
- no “bigger spheres work” non-answer
- no silent claim upgrades to physical blocking

## Done Condition

The task is done only when the ranked report, status page, and supporting
diagnostics all agree on the mechanism story and recommended honest next step.
