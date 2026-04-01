# Evaluator Rubric

This rubric is for a separate reviewer/evaluator pass after generation or
implementation.

## Dimensions

### 1. Functionality

- Does the claimed workflow actually run?
- Are the expected artifacts present?
- Are required fields present in outputs?

### 2. Architecture / Scope Discipline

- Did the change stay within allowed write scope?
- Did it avoid unnecessary scope expansion?
- Did it preserve the read-only Newton core boundary?

### 3. Operability

- Are commands reproducible?
- Is the output directory structure understandable?
- Are logs and command traces written out?

### 4. Presentation / Communication

- Can another engineer find the relevant task page quickly?
- Is the status/doc update sufficient for the next agent?
- Are conclusions separated from raw outputs?

## Pass Rule

A task is not truly done if any one of these dimensions fails in a material way.
