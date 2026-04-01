# Bridge Task Pages Rules

These pages are the durable task-facing source of truth.

## Rule

Each active task page should map to one canonical slug and one execution chain:

task page -> spec -> plan -> implement -> status -> latest result pointer

The committed latest-result pointer should live in `results_meta/` when the
task has authoritative local result bundles.

## Keep Pages Focused

- explain the task question and claim boundary
- link to result roots instead of copying large run notes
- mark deprecated task families explicitly rather than leaving duplicates alive
