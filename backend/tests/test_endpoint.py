import io
import time

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _poll(job_id: str, timeout: float = 10.0) -> dict:
    """잡이 done 이 될 때까지 폴링해 result 를 반환한다."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = client.get(f"/api/analyze-status/{job_id}")
        assert res.status_code == 200
        body = res.json()
        if body["status"] == "done":
            return body["result"]
        assert body["status"] == "running"
        assert isinstance(body["step"], int)
        time.sleep(0.05)
    raise AssertionError("잡이 제한 시간 안에 끝나지 않았습니다")


def test_analyze_contract_success_pdf():
    files = [("files", ("contract.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf"))]
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    job_id = res.json()["jobId"]
    body = _poll(job_id)
    assert body["status"] == "success"
    assert len(body["data"]["riskAssessments"]) == 9


def test_analyze_contract_bundle():
    files = [
        ("files", ("contract.pdf", io.BytesIO(b"%PDF-1.4 c"), "application/pdf")),
        ("files", ("등기부등본.pdf", io.BytesIO(b"%PDF-1.4 r"), "application/pdf")),
    ]
    res = client.post("/api/analyze-contract", files=files)
    assert res.status_code == 200
    body = _poll(res.json()["jobId"])
    assert body["status"] == "success"
    assert "등기부등본" in body["data"]["providedDocuments"]


def test_analyze_status_unknown_job_returns_404():
    res = client.get("/api/analyze-status/no-such-job")
    assert res.status_code == 404


def test_analyze_status_result_is_destroyed_after_first_read():
    files = [("files", ("contract.pdf", io.BytesIO(b"%PDF-1.4 once"), "application/pdf"))]
    job_id = client.post("/api/analyze-contract", files=files).json()["jobId"]
    body = _poll(job_id)
    assert body["status"] == "success"
    # 서버 무저장 원칙: 결과는 첫 전달 즉시 파기되므로 재조회는 404
    res = client.get(f"/api/analyze-status/{job_id}")
    assert res.status_code == 404


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
