# M0 Done

- Initialized `invstruct` as a standalone Python package under `src/invstruct`.
- Added baseline CLI (`invstruct parse`, `invstruct health`) and FastAPI app (`/healthz`, `/v1/parse`).
- Added unified error payload contract and invoice schema roundtrip helpers.
- Added deterministic utilities (`trace_id`, `sha256_file`) and settings loading.
- Added baseline unit tests for hash, trace, schema, config, API, and CLI.
