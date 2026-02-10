from __future__ import annotations

import hashlib

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import JSONResponse

from invstruct import __version__
from invstruct.contracts.export_schema import get_export_contract_schema
from invstruct.contracts.record_schema import get_invoice_record_json_schema
from invstruct.errors import error_payload
from invstruct.schema_version import EXPORT_SCHEMA_VERSION, RECORD_SCHEMA_VERSION
from invstruct.schemas import InvoiceRecord, SourceInfo
from invstruct.utils.trace import generate_trace_id

app = FastAPI(title="invstruct")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/meta/contracts")
def meta_contracts() -> dict[str, object]:
    return {
        "tool_version": __version__,
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
    }


@app.get("/v1/meta/contracts/record-schema", response_model=None)
def meta_contract_record_schema() -> dict:
    return get_invoice_record_json_schema()


@app.get("/v1/meta/contracts/export-schema", response_model=None)
def meta_contract_export_schema() -> dict:
    return get_export_contract_schema()


@app.post("/v1/parse")
async def parse_file(
    file: UploadFile = File(...),
    allow_pdf: bool = Query(False),
) -> dict:
    trace_id = generate_trace_id()
    filename = file.filename or "unknown"
    content = await file.read()
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf" and not allow_pdf:
        return JSONResponse(
            status_code=400,
            content=error_payload(
                code="E3001",
                message="PDF not supported yet",
                trace_id=trace_id,
                details={"file_name": filename},
            ),
        )
    record = InvoiceRecord(
        source=SourceInfo(
            file_name=filename,
            sha256=hashlib.sha256(content).hexdigest(),
            trace_id=trace_id,
        ),
        status="success",
    )
    return record.model_dump()
