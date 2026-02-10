import json

from typer.testing import CliRunner

from invstruct.cli import app
from invstruct.schema_version import EXPORT_SCHEMA_VERSION, RECORD_SCHEMA_VERSION


def test_contract_show_contains_versions() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["contract", "show"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip())
    assert payload["record_schema_version"] == RECORD_SCHEMA_VERSION
    assert payload["export_schema_version"] == EXPORT_SCHEMA_VERSION
    assert "tool_version" in payload


def test_contract_schema_record_contains_id() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["contract", "schema", "record"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip())
    assert payload["$id"] == f"invstruct/record-schema/v{RECORD_SCHEMA_VERSION}"
    assert payload["schema_version"] == RECORD_SCHEMA_VERSION
