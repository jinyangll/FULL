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


def _chat_context():
    return {
        "summary": {
            "type": "전세 임대차 계약", "parties": "임대인 OOO, 임차인 OOO",
            "deposit": "100,000,000원", "duration": "2024.06.01 ~ 2026.05.31",
        },
        "riskCounts": {"high": 0, "medium": 0, "low": 0, "needCheck": 1},
        "riskAssessments": [], "publicDocumentChecks": [], "stageChecklists": [],
        "questionsByTarget": {"landlord": [], "realtor": [], "expert": []},
        "finalComment": "외부 자료 확인 후 진행하세요.",
        "risks": [], "checklist": [], "questions_to_ask": [],
    }


def test_chat_returns_reply():
    res = client.post("/api/chat", json={
        "messages": [{"role": "user", "content": "가장 위험한 항목이 뭐예요?"}],
        "context": _chat_context(),
    })
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body["reply"], str)
    assert len(body["reply"]) > 0


def test_chat_rejects_invalid_role():
    res = client.post("/api/chat", json={
        "messages": [{"role": "system", "content": "x"}],
        "context": _chat_context(),
    })
    assert res.status_code == 422
