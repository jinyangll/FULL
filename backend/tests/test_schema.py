from app.schema import (
    AnalysisResponse, AnalysisData, AnalysisSummary, RiskAssessment,
    ChatMessage, ChatRequest, ChatResponse,
)


def test_success_response_serializes_camelcase():
    summary = AnalysisSummary(
        type="전세 임대차 계약", parties="임대인 OOO, 임차인 OOO",
        deposit="100,000,000원", duration="2024.06.01 ~ 2026.05.31",
    )
    assessment = RiskAssessment(
        id="jeonse-price-ratio", title="전세가율 과다", level="확인 필요",
        status="외부 서류 확인 필요", category="보증금 리스크",
        requiredDocuments=["계약서 보증금"], contractClues=["보증금"],
        whyImportant="...", currentFinding="...", action="...",
        questions=["..."], stages=["물건 탐색"],
    )
    data = AnalysisData(
        summary=summary, riskCounts={"high": 0, "medium": 0, "low": 0,
        "needCheck": 1}, riskAssessments=[assessment],
        publicDocumentChecks=[], stageChecklists=[], questionsByTarget={
        "landlord": [], "realtor": [], "expert": []}, finalComment="...",
        risks=[], checklist=[], questions_to_ask=[],
    )
    resp = AnalysisResponse(status="success", data=data)
    dumped = resp.model_dump(exclude_none=True)
    assert dumped["status"] == "success"
    assert dumped["data"]["riskAssessments"][0]["requiredDocuments"] == ["계약서 보증금"]
    assert "questions_to_ask" in dumped["data"]


def test_error_response():
    resp = AnalysisResponse(status="error", error={"code": "not_contract", "message": "x"})
    dumped = resp.model_dump(exclude_none=True)
    assert dumped["error"]["code"] == "not_contract"
    assert "data" not in dumped


def _sample_analysis_data() -> AnalysisData:
    summary = AnalysisSummary(
        type="전세 임대차 계약", parties="임대인 OOO, 임차인 OOO",
        deposit="100,000,000원", duration="2024.06.01 ~ 2026.05.31",
    )
    return AnalysisData(
        summary=summary, riskCounts={"high": 0, "medium": 0, "low": 0, "needCheck": 1},
        riskAssessments=[], publicDocumentChecks=[], stageChecklists=[],
        questionsByTarget={"landlord": [], "realtor": [], "expert": []},
        finalComment="...", risks=[], checklist=[], questions_to_ask=[],
    )


def test_chat_request_accepts_messages_and_context():
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="가장 위험한 항목은?")],
        context=_sample_analysis_data(),
    )
    assert req.messages[0].role == "user"
    assert req.context.summary.deposit == "100,000,000원"


def test_chat_message_rejects_invalid_role():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ChatMessage(role="system", content="x")


def test_chat_response_serializes_reply():
    resp = ChatResponse(reply="전세가율을 먼저 확인하세요.")
    assert resp.model_dump()["reply"] == "전세가율을 먼저 확인하세요."
