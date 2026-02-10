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

## M1.10: CI triage acceleration and release gate

### Done
- Enhanced CI workflows to publish richer `$GITHUB_STEP_SUMMARY` diagnostics for pytest, schema policy, and contract gates.
- Added machine-readable `ci_gate_report.json` artifact output and upload for gate triage.
- Added tag-triggered `release-gate.yml` workflow to enforce test/policy/contract checks before release.
- Added tests for gate report generation and tag-mode schema policy logic.

### Next
- Add PR-level annotations that link directly to failing command snippets in artifacts.
- Extend release gate to verify changelog consistency with schema/version metadata.

## M1.11: PR annotations and release changelog gate

### Done
- Added CI annotation emitter (`scripts/emit_ci_annotations.py`) to map gate report failures into GitHub log annotations.
- Wired CI workflow to emit annotations on every run and keep gate semantics unchanged.
- Added changelog consistency checker (`scripts/check_changelog_consistency.py`) and integrated it into tag release gate.
- Added regression tests for annotation limits/ok-notice behavior and changelog consistency checks.

### Next
- Add file-level annotation mapping from command stderr patterns to improve triage accuracy.
- Extend changelog check to validate subsection templates per release type.
