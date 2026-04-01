# Archive Policy

This subtree is reserved for explicit historical archives.

## When To Archive

Archive a Markdown surface when:

- it still has historical value,
- it should no longer sound current,
- and an in-place deprecated stub would be too noisy or misleading.

## Archive Rule

Archived files must begin with:

- `status: historical`
- `canonical_replacement: ...` or `none`
- `owner_surface: ...`
- `last_reviewed: ...`
- `notes: ...`

Archived files are not live control-plane instructions. They exist to preserve
history, not to route current work.
