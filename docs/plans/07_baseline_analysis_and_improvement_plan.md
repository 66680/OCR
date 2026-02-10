# 07 Baseline Analysis And Improvement Plan

## Done
- M0 baseline initialized in `invstruct-main` branch with installable package layout.
- Added stable baseline CLI/API contracts and unified error payload.
- Added baseline regression tests to ensure local reproducibility.
- M1.8 contract governance completed with `record_schema_version`, contract JSON schemas, and validation entry points.
- Added CLI/API contract endpoints for downstream machine validation.
- Added regression tests to lock schema stability and export contract checks.
- Added M1.9 CI workflow gates with pytest + contract gate scripts on push/pull_request.
- Added schema bump policy script to require Migration Notes when schema version constants change.
- Added regression tests for CI gate script behavior and schema bump policy logic.
- Added M1.10 CI summary enhancements with failure-tail diagnostics and local reproduce hints.
- Added gate report artifact (`out/ci_gate_report.json`) emission and workflow upload for PR triage.
- Added release gate workflow for tag pushes (`v*`) enforcing tests + schema policy + contract gates.
- Added regression tests for gate report persistence and tag-mode policy checks.

## Next
- Add GitHub Checks annotations mapped from gate report failed steps for one-click triage.
- Add signed release pipeline wiring after release gate success.
