# Release Send PDF Runbook

## Purpose

External sending is a release step, not a build step.

## Sensitive Script

- `scripts/send_pdf_via_yahoo.py`

Tracked example config:

- `scripts/send_pdf_via_yahoo.local.example.json`

## Rule

Never run it automatically without explicit human approval.

## Before Sending

1. validate the final PDF/output bundle
2. confirm recipients and intent
3. record the release decision in a status log or decision record

## If Approval Is Missing

Stop and report that release is blocked.
