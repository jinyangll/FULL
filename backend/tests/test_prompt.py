from app.prompt import build_messages
from app.scaffold import RISK_IDS


def test_messages_shape_and_content():
    msgs = build_messages("계약서 본문 텍스트", {"deposit": "1억원"}, [])
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    joined = " ".join(m["content"] for m in msgs)
    for rid in RISK_IDS:
        assert rid in joined
    assert "계약서 본문 텍스트" in joined
    assert "1억원" in joined
    assert "JSON" in joined


def test_prompt_requests_evidence_quotes():
    msgs = build_messages("계약서 본문 텍스트", {"deposit": "1억원"}, [])
    user = msgs[-1]["content"]
    assert "evidence" in user
    assert "그대로 인용" in user
    assert "만들어 넣지 말 것" in user  # 환각 인용 금지 지침


def test_supporting_docs_and_rules_in_prompt():
    from app.prompt import build_messages
    msgs = build_messages(
        "계약서 본문",
        {"type": "전세"},
        [("등기부등본", "갑구 소유자 홍길동")],
    )
    user = msgs[1]["content"]
    assert "등기부등본" in user
    assert "갑구 소유자 홍길동" in user
    assert "판별 규칙" in user
    assert "추측하지 말고" in user


def test_no_supporting_docs_notes_absence():
    from app.prompt import build_messages
    msgs = build_messages("계약서 본문", {"type": "전세"}, [])
    user = msgs[1]["content"]
    assert "제출되지 않았습니다" in user


_JEONSE = {
    "level": "높음",
    "status": "조건부 해당",
    "currentFinding": "국토교통부 실거래가 19건 기준 시세 약 4억 2,500만원, 보증금은 시세의 99%입니다.",
    "action": "보증보험 가입 가능 여부를 확인하세요.",
    "dataSource": "국토교통부 실거래가 19건 기준",
}


def test_jeonse_result_injected_when_present():
    msgs = build_messages("계약서 본문", {"type": "전세"}, [], _JEONSE)
    user = msgs[1]["content"]
    assert "실거래가 자동조회 결과" in user
    assert "99%" in user
    assert "추측" in user  # 추측 표현 금지 지침


def test_no_jeonse_block_when_absent():
    msgs = build_messages("계약서 본문", {"type": "전세"}, [], None)
    assert "실거래가 자동조회 결과" not in msgs[1]["content"]


_LANDLORD = {
    "level": "높음",
    "status": "외부 서류 확인 필요",
    "currentFinding": (
        "등기부 소유자 고웅주(만 33세, 서울 서대문구 성산로 309-29)이 HUG 상습채무불이행자 "
        "공개 명단의 인적사항과 일치합니다. 반환채무 약 1,032,000,000원(기준일 2026-01-27)."
    ),
    "action": "안심전세포털 상습채무불이행자 명단에서 직접 대조하세요.",
    "dataSource": "HUG 상습채무불이행자 명단(기준일 2026-01-27) 대조",
}


def test_blacklist_block_injected_when_present():
    msgs = build_messages("계약 본문", {"type": "전세"}, [], landlord=_LANDLORD)
    user = msgs[1]["content"]
    assert "악성임대인 명단 대조 결과" in user
    assert "2026-01-27" in user


def test_no_blacklist_block_when_absent():
    msgs = build_messages("계약 본문", {"type": "전세"}, [])
    assert "악성임대인 명단 대조 결과" not in msgs[1]["content"]
