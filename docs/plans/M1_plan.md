# M1 Plan

## M1.8: downstream contract governance

### Done
- Added `RECORD_SCHEMA_VERSION=1` and aligned `EXPORT_SCHEMA_VERSION=1` governance constants.
- Added contract artifacts for record/export schemas under `src/invstruct/contracts`.
- Added CLI contract commands for show/schema/validate-records/validate-export.
- Added API meta endpoints for contract versions and JSON schemas.
- Added regression tests for schema defaults, deterministic schema output, CLI contract flows, export validation, and API contract endpoints.

### Next
- Integrate contract validation into CI workflow gates for pull requests.
- Add release checklist to bump schema versions only with explicit migration notes.

## M1.9: CI workflow gates and schema bump policy

### Done
- Added GitHub Actions CI workflow for `push` and `pull_request` with Python 3.11/3.12 matrix.
- Added automated contract gates script to generate temporary records/export artifacts and validate them.
- Added schema bump policy checker that blocks schema version number changes without migration notes.
- Added regression tests for CI contract gate script logic and schema bump policy regex evaluation.

### Next
- Add PR annotation output for failed contract gates to speed up triage.
- Add a release checklist item to explicitly confirm migration notes quality when schema versions change.
