import hashlib
import json

from invstruct.contracts.record_schema import get_invoice_record_json_schema


def test_record_schema_is_deterministic_with_fixed_timestamp() -> None:
    generated_at = "2026-02-10T00:00:00+00:00"
    first = get_invoice_record_json_schema(generated_at=generated_at)
    second = get_invoice_record_json_schema(generated_at=generated_at)

    first_serialized = json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    second_serialized = json.dumps(second, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    first_hash = hashlib.sha256(first_serialized.encode("utf-8")).hexdigest()
    second_hash = hashlib.sha256(second_serialized.encode("utf-8")).hexdigest()

    assert first_hash == second_hash
    assert first_serialized == second_serialized
