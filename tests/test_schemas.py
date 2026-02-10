from invstruct.schemas import FieldProvenance, InvoiceRecord, SourceInfo


def test_invoice_record_roundtrip() -> None:
    record = InvoiceRecord(
        source=SourceInfo(file_name="a.png", sha256="f" * 64, trace_id="t1"),
        merchant="Shop",
        confidence={"merchant": 0.95},
        provenance=[FieldProvenance(page=1, line_id="l1", line_text="Shop")],
        status="success",
    )
    encoded = record.to_json()
    decoded = InvoiceRecord.from_json(encoded)
    assert decoded.source.file_name == "a.png"
    assert decoded.merchant == "Shop"
    assert decoded.confidence["merchant"] == 0.95
    assert decoded.provenance[0].line_text == "Shop"
