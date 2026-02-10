from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from invstruct.schema_version import RECORD_SCHEMA_VERSION


class FieldProvenance(BaseModel):
    page: int | None = None
    bbox: list[float] | None = None
    line_id: str | None = None
    line_text: str | None = None


class SourceInfo(BaseModel):
    file_name: str
    sha256: str
    trace_id: str


class InvoiceRecord(BaseModel):
    source: SourceInfo
    record_schema_version: int = RECORD_SCHEMA_VERSION
    merchant: str | None = None
    issue_date: str | None = None
    total_amount_gross: float | None = None
    currency: str | None = None
    invoice_number: str | None = None
    tax_number: str | None = None
    confidence: dict[str, float] = Field(default_factory=dict)
    provenance: list[FieldProvenance] = Field(default_factory=list)
    status: Literal["success", "failed", "skipped"] = "success"
    error_code: str | None = None
    error_message: str | None = None
    warnings: list[dict[str, Any]] = Field(default_factory=list)
    retry_key: str | None = None
    parser_version: str | None = None

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, payload: str) -> "InvoiceRecord":
        return cls.model_validate_json(payload)
