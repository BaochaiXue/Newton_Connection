---
name: release-gate
description: Gate external side effects such as email sending or final release actions. Use when a task is about sending PDFs, publishing outputs, or triggering actions outside the local repo.
---

# Release Gate

## Purpose

External side effects are not the same as local validation.

## Hard Rule

Do not send email or trigger equivalent external actions without explicit human
approval.

## Sensitive Entry Points

- `send_pdf_via_yahoo.py`

## Required Checklist Before Release

1. artifact generation completed
2. validation completed
3. output paths recorded
4. human approval explicitly granted

## Reporting Rule

If approval is missing, stop and say release is blocked pending approval.
