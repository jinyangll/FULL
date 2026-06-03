from app.schema import AnalysisResponse, AnalysisData, AnalysisSummary, RiskAssessment


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
