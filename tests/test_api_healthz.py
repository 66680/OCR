from fastapi.testclient import TestClient

from invstruct.api.app import app


def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parse_pdf_default_rejects() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/parse",
        files={"file": ("sample.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["code"] == "E3001"
    assert payload["error"]["message"] == "PDF not supported yet"
