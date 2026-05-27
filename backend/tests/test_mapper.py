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
    data = build_data(summary, llm)
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
    data = build_data(summary, llm)
    target = next(a for a in data.riskAssessments if a.id == "jeonse-price-ratio")
    assert target.level == "확인 필요"          # 기본값으로 보정
    assert target.status == "외부 서류 확인 필요"  # 기본값으로 보정
