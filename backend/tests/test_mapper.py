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
        {"level": "확인 필요"}, {"level": "판단 불가"}, {"level": "고위험"},
    ]
    counts = count_levels(assessments)
    assert counts == {"high": 2, "medium": 1, "low": 1, "needCheck": 1, "unknown": 1}


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


def test_build_data_coerces_invalid_level_and_status():
    """LLM 이 enum 을 벗어난 값을 줘도 기본값으로 보정해 검증 통과한다."""
    summary = {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    llm = {"assessments": {"jeonse-price-ratio": {
        "level": "위험함",          # 허용 외 level
        "status": "판단 불가",       # level 값을 status 칸에 잘못 넣음
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
