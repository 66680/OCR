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
