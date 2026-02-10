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
- Added M1.11 PR-level gate annotations sourced from `ci_gate_report.json` with configurable limits.
- Added release changelog consistency gate and JSON report artifact (`out/changelog_report.json`).
- Added regression tests for annotation rendering limits/notice mode and changelog policy outcomes.

## Next
- Add smarter annotation routing with file/line hints where parser output allows.
- Add signed release pipeline wiring after release gate success.

## Done (release bundle artifact filtering sync)
- Synced release packaging patch into git repo workspace from delivery workspace.
- Added `scripts/package_release.py` with version-aware dist artifact picking:
  - include only `invstruct-<version>-*.whl`
  - include only `invstruct-<version>.tar.gz`
- Added regression test `tests/test_package_release_filters_current_version.py` to prevent historical dist artifacts leaking into current release bundle.

## Next (release pipeline alignment)
- Backport missing M3-0/M3-1 release automation files (`release.ps1`, `release_check.py`, `dump_openapi.py`, release docs) into this git repo.
- Run full release rehearsal in this git repo after release automation alignment.
