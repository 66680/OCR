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

## Next
- Add CI summary annotations to surface which contract gate failed directly in PR checks.
- Add release automation that ties schema version bumps to tagged migration notes templates.
