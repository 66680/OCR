from invstruct.schema_version import RECORD_SCHEMA_VERSION
from invstruct.schemas import InvoiceRecord, SourceInfo


def test_record_schema_version_default() -> None:
    record = InvoiceRecord(
        source=SourceInfo(file_name="a.png", sha256="f" * 64, trace_id="t1"),
    )
    assert record.record_schema_version == RECORD_SCHEMA_VERSION


def test_record_schema_version_backfill_for_legacy_payload() -> None:
    payload = {
        "source": {"file_name": "legacy.png", "sha256": "a" * 64, "trace_id": "t2"},
        "merchant": "Legacy Shop",
    }
    record = InvoiceRecord.model_validate(payload)
    assert record.record_schema_version == RECORD_SCHEMA_VERSION
