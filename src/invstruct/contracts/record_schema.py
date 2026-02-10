from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from invstruct import __version__
from invstruct.schema_version import RECORD_SCHEMA_VERSION
from invstruct.schemas import InvoiceRecord


def get_invoice_record_json_schema(generated_at: str | None = None) -> dict[str, Any]:
    schema = InvoiceRecord.model_json_schema()
    schema["$id"] = f"invstruct/record-schema/v{RECORD_SCHEMA_VERSION}"
    schema["schema_version"] = RECORD_SCHEMA_VERSION
    schema["generated_at"] = generated_at or datetime.now(UTC).isoformat()
    schema["tool_version"] = __version__
    return schema
