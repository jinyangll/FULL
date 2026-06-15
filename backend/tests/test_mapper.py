import pytest
from app.mapper import is_contract, parse_llm_json, count_levels, build_data
from app.scaffold import RISK_IDS


def test_is_contract():
    assert is_contract("임대차계약서") is True
    assert is_contract("전월세 임대차 계약서") is True
    assert is_contract("졸업증명서") is False


def test_parse_llm_json_strips_code_fence():
    raw = '```json\n{"assessments": {}, "finalComment": "x"}\n```'
    parsed = parse_llm_json(raw)
    assert parsed["finalComment"] == "x"


def test_parse_llm_json_raises_on_garbage():
    with pytest.raises(ValueError):
        parse_llm_json("이건 JSON 이 아닙니다")


def test_count_levels_maps_to_buckets():
    assessments = [
        {"level": "높음"}, {"level": "주의"}, {"level": "낮음"},
        {"level": "확인 필요"}, {"level": "고위험"},
    ]
    counts = count_levels(assessments)
    assert counts == {"high": 2, "medium": 1, "low": 1, "needCheck": 1}


def test_count_levels_unknown_level_falls_back_to_needcheck():
    # 허용 외 level(과거 '판단 불가' 포함)은 '확인 필요' 버킷으로 흡수된다
    counts = count_levels([{"level": "판단 불가"}, {"level": "이상한값"}])
    assert counts == {"high": 0, "medium": 0, "low": 0, "needCheck": 2}


def test_build_data_always_has_nine_categories_even_if_llm_partial():
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {"jeonse-price-ratio": {
        "level": "높음", "status": "외부 서류 확인 필요",
        "currentFinding": "전세가율 높음", "action": "확인", "questions": ["q"]}},
        "finalComment": "총평"}
    data = build_data(summary, llm, [])
    ids = [a.id for a in data.riskAssessments]
    assert ids == RISK_IDS
    missing = next(a for a in data.riskAssessments if a.id == "trust-registration")
    assert missing.level == "확인 필요"
    assert data.riskCounts.high >= 1
    assert data.finalComment == "총평"


def test_build_data_carries_evidence():
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {"jeonse-price-ratio": {
        "level": "높음", "status": "외부 서류 확인 필요",
        "currentFinding": "x", "action": "y", "questions": ["q"],
        "evidence": ["보증금 육억팔천만원", "  특약 제3조  ", ""]}},
        "finalComment": "총평"}
    data = build_data(summary, llm, [])
    target = next(a for a in data.riskAssessments if a.id == "jeonse-price-ratio")
    assert target.evidence == ["보증금 육억팔천만원", "특약 제3조"]  # 공백·빈 문자열 정리
    missing = next(a for a in data.riskAssessments if a.id == "trust-registration")
    assert missing.evidence == []  # LLM 미응답 카테고리는 빈 배열


def test_build_data_evidence_coerces_garbage():
    """evidence 가 리스트가 아니거나 4개 이상이어도 안전하게 보정한다."""
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {"jeonse-price-ratio": {
        "level": "높음", "status": "외부 서류 확인 필요",
        "currentFinding": "x", "action": "y", "questions": ["q"],
        "evidence": "원문 한 줄"},  # 리스트가 아님
        "special-clause-risk": {
        "level": "주의", "status": "계약서에서 확인됨",
        "currentFinding": "x", "action": "y", "questions": ["q"],
        "evidence": ["a", "b", "c", "d", "e"]}},
        "finalComment": "총평"}
    data = build_data(summary, llm, [])
    jeonse = next(a for a in data.riskAssessments if a.id == "jeonse-price-ratio")
    special = next(a for a in data.riskAssessments if a.id == "special-clause-risk")
    assert jeonse.evidence == []
    assert special.evidence == ["a", "b", "c"]  # 최대 3개


def test_build_data_coerces_invalid_level_and_status():
    """LLM 이 enum 을 벗어난 값을 줘도 기본값으로 보정해 검증 통과한다."""
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {"jeonse-price-ratio": {
        "level": "위험함",          # 허용 외 level
        "status": "판단 불가",       # 허용 외 status (구 enum 제거됨)
        "currentFinding": "x", "action": "y", "questions": ["q"]}},
        "finalComment": "총평"}
    data = build_data(summary, llm, [])
    target = next(a for a in data.riskAssessments if a.id == "jeonse-price-ratio")
    assert target.level == "확인 필요"          # 기본값으로 보정
    assert target.status == "외부 서류 확인 필요"  # 기본값으로 보정


def test_build_data_includes_provided_documents():
    from app.mapper import build_data
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {}, "finalComment": "총평"}
    data = build_data(summary, llm, ["임대차계약서", "등기부등본"])
    assert data.providedDocuments == ["임대차계약서", "등기부등본"]


def _basic(provided):
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    return build_data(summary, {"assessments": {}, "finalComment": ""}, provided)


def test_public_doc_checks_exclude_provided_registry():
    # 등기부등본을 올렸으면 '추가로 확인해야 할 서류'에서 빠진다
    data = _basic(["임대차계약서", "등기부등본"])
    names = [c.name for c in data.publicDocumentChecks]
    assert "등기부등본" not in names


def test_public_doc_checks_match_label_alias():
    # 분류 라벨(미납국세열람내역/중개대상물확인서)과 목록 이름이 달라도 제외된다
    data = _basic(["임대차계약서", "미납국세열람내역", "중개대상물확인서"])
    names = [c.name for c in data.publicDocumentChecks]
    assert "미납 국세·지방세 열람" not in names
    assert "중개대상물 확인·설명서" not in names


def test_public_doc_checks_keep_online_only_item():
    # 실거래가/안심전세 App 은 업로드 대상이 아니므로 항상 남는다
    data = _basic(["임대차계약서", "등기부등본"])
    names = [c.name for c in data.publicDocumentChecks]
    assert any("안심전세" in n for n in names)


def test_public_doc_checks_full_list_when_only_contract():
    # 계약서만 올리면 7개 전부 유지
    data = _basic(["임대차계약서"])
    assert len(data.publicDocumentChecks) == 7


def test_realprice_item_trimmed_when_resolved():
    # 전세가율 자동조회 성공 시 '실거래가 공개시스템' 항목을 안심전세 App 으로 다듬는다
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    data = build_data(summary, {"assessments": {}, "finalComment": ""}, ["임대차계약서"], realprice_resolved=True)
    names = [c.name for c in data.publicDocumentChecks]
    assert "실거래가 공개시스템 / 안심전세 App" not in names
    assert "안심전세 App" in names
    item = next(c for c in data.publicDocumentChecks if c.name == "안심전세 App")
    assert "전세가율" not in item.checks
    assert "최근 매매 실거래가" not in item.checks


def test_realprice_item_intact_when_not_resolved():
    data = _basic(["임대차계약서"])
    names = [c.name for c in data.publicDocumentChecks]
    assert "실거래가 공개시스템 / 안심전세 App" in names


def test_public_doc_importance_follows_risk_level():
    # 공적서류 중요도는 연결된 위험 항목의 위험도에 따라 동적으로 매겨진다
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {
        "jeonse-price-ratio": {"level": "높음", "status": "외부 서류 확인 필요",
            "currentFinding": "x", "action": "y", "questions": ["q"]},
        "building-legality": {"level": "낮음", "status": "계약서에서 확인됨",
            "currentFinding": "x", "action": "y", "questions": ["q"]},
    }, "finalComment": ""}
    data = build_data(summary, llm, ["임대차계약서"])
    by_name = {c.name: c for c in data.publicDocumentChecks}
    # 실거래가/안심전세 → jeonse-price-ratio(높음) → 높음
    assert by_name["실거래가 공개시스템 / 안심전세 App"].importance == "높음"
    # 건축물대장 → building-legality(낮음) → 낮음
    assert by_name["건축물대장"].importance == "낮음"
    # 미제공 위험(landlord-tax-arrears)은 기본 '확인 필요' → 보통
    assert by_name["미납 국세·지방세 열람"].importance == "보통"


def test_public_doc_importance_not_all_high():
    # 회귀 방지: 더 이상 모든 서류가 '높음'으로 고정되지 않는다
    data = _basic(["임대차계약서"])  # 빈 assessments → 전부 기본 '확인 필요'
    importances = {c.importance for c in data.publicDocumentChecks}
    assert importances == {"보통"}  # 확인 필요 → 보통
