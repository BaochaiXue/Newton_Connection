> status: canonical
> canonical_replacement: none
> owner_surface: `results_registry`
> last_reviewed: `2026-04-01`
> review_interval: `30d`
> update_rule: `Update when registry field requirements or authority semantics change.`
> notes: Canonical schema for committed result-authority entries under results_meta/tasks/.

# Results Metadata Schema

Version: `1`

Each task entry under `results_meta/tasks/` must include:

## Top-Level Fields

- `registry_version`
- `task_slug`
- `task_chain`
- `bundle_root`
- `authoritative_run`
- `superseded_runs`
- `local_only_surfaces`
- `updated_at`

## `task_chain`

- `task_page`
- `spec`
- `plan`
- `implement`
- `status`

All values must be repo-relative paths.

## `authoritative_run`

- `run_id`
- `authoritative`
- `task_state`
  - expected values:
    - `promoted`
    - `blocked`
    - `partial`
    - `historical`
- `claim_boundary`
- `local_artifact_root`
- `command_pointer`
- `expected_artifacts`
- `validator_outputs`
- `verdict_pointers`
- `repo_friendly_evidence`
- `why_passed`
- `predecessor`
- `superseded_by`

## `superseded_runs[]`

Each object should include:

- `run_id`
- `status`
- `local_artifact_root`
- `why_not_authoritative`
- `superseded_by`

## `local_only_surfaces`

List local or ignored bundle files that may still exist for convenience but are
not the canonical committed truth surface.

## Notes

- Use repo-relative paths even when the local bundle docs use absolute paths.
- `authoritative = false` is allowed when a task is currently blocked or only
  partially promoted, but the current focus bundle still needs to be discoverable.
