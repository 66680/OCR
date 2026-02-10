# 07 Baseline Analysis And Improvement Plan

## Done
- M0 baseline initialized in `invstruct-main` branch with installable package layout.
- Added stable baseline CLI/API contracts and unified error payload.
- Added baseline regression tests to ensure local reproducibility.
- M1.8 contract governance completed with `record_schema_version`, contract JSON schemas, and validation entry points.
- Added CLI/API contract endpoints for downstream machine validation.
- Added regression tests to lock schema stability and export contract checks.

## Next
- Add CI checks to run contract validation against golden samples before merge.
- Add release automation to enforce schema-version bump policy and changelog notes.
