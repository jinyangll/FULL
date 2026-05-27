import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_contract_success_pdf():
    files = {"file": ("contract.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert len(body["data"]["riskAssessments"]) == 9
    assert body["data"]["riskCounts"]["needCheck"] >= 1


def test_analyze_contract_unsupported_format():
    files = {"file": ("note.txt", io.BytesIO(b"hello"), "text/plain")}
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "unsupported_format"
