import json
from pathlib import Path

from typer.testing import CliRunner

from invstruct.cli import app
from invstruct.schemas import InvoiceRecord, SourceInfo


def test_validate_records_reports_invalid_lines(tmp_path: Path) -> None:
    valid_record = InvoiceRecord(
        source=SourceInfo(file_name="a.png", sha256="f" * 64, trace_id="trace-a"),
        merchant="Store A",
    )
    compat_record = {
        "source": {
            "file_name": "legacy.png",
            "sha256": "a" * 64,
            "trace_id": "trace-legacy",
        },
        "merchant": "Legacy",
    }
    records_path = tmp_path / "records.jsonl"
    records_path.write_text(
        "\n".join(
            [
                valid_record.model_dump_json(),
                json.dumps(compat_record, ensure_ascii=False),
                "{bad-json}",
            ]
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(app, ["contract", "validate-records", str(records_path)])
    assert result.exit_code == 2
    payload = json.loads(result.stdout.strip())
    assert payload["error"]["code"] == "E5002"
    summary = payload["error"]["details"]["summary"]
    assert summary["total"] == 3
    assert summary["ok"] == 2
    assert summary["invalid"] == 1
