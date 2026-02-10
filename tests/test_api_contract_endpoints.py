from fastapi.testclient import TestClient

from invstruct.api.app import app
from invstruct.schema_version import EXPORT_SCHEMA_VERSION, RECORD_SCHEMA_VERSION


def test_api_contract_meta_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/v1/meta/contracts")
    assert response.status_code == 200
    payload = response.json()
    assert payload["record_schema_version"] == RECORD_SCHEMA_VERSION
    assert payload["export_schema_version"] == EXPORT_SCHEMA_VERSION
    assert "tool_version" in payload


def test_api_contract_record_schema_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/v1/meta/contracts/record-schema")
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == RECORD_SCHEMA_VERSION
    assert payload["$id"] == f"invstruct/record-schema/v{RECORD_SCHEMA_VERSION}"


def test_api_contract_export_schema_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/v1/meta/contracts/export-schema")
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == EXPORT_SCHEMA_VERSION
    assert "required_columns" in payload
