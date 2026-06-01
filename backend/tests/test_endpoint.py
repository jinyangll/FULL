import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_contract_success_pdf():
    files = [("files", ("contract.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf"))]
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert len(body["data"]["riskAssessments"]) == 9


def test_analyze_contract_bundle():
    files = [
        ("files", ("contract.pdf", io.BytesIO(b"%PDF-1.4 c"), "application/pdf")),
        ("files", ("등기부등본.pdf", io.BytesIO(b"%PDF-1.4 r"), "application/pdf")),
    ]
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert "등기부등본" in body["data"]["providedDocuments"]


def test_analyze_contract_unsupported_format():
    files = [("files", ("note.txt", io.BytesIO(b"hello"), "text/plain"))]
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "unsupported_format"
