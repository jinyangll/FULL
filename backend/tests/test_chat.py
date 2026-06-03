from app.chat import build_chat_messages

_CONTEXT = {
    "summary": {
        "type": "전세 임대차 계약",
        "parties": "임대인 김철수, 임차인 박준혁",
        "deposit": "420,000,000원",
        "monthlyRent": "없음",
        "duration": "2026.07.01 ~ 2028.06.30",
        "maintenanceFee": "월 80,000원",
        "realtor": "OO공인중개사무소, 중개사 이영희",
        "address": "서울특별시 종로구 청운동 1-1",
    },
    "riskAssessments": [
        {
            "title": "전세가율 과다",
            "level": "높음",
            "status": "조건부 해당",
            "currentFinding": "보증금이 시세의 99%입니다.",
            "action": "보증보험 가입 가능 여부를 확인하세요.",
        }
    ],
    "finalComment": "전세가율이 높아 주의가 필요합니다.",
    "checklist": ["등기부등본 확인", "확정일자 받기"],
}


def test_system_message_includes_context():
    msgs = build_chat_messages(
        [{"role": "user", "content": "가장 위험한 항목이 뭐예요?"}], _CONTEXT
    )
    assert msgs[0]["role"] == "system"
    system = msgs[0]["content"]
    assert "전세가율 과다" in system
    assert "보증금이 시세의 99%입니다." in system
    assert "전세가율이 높아 주의가 필요합니다." in system


def test_system_message_includes_parties_and_summary_facts():
    """임차인·임대인·중개사 등 계약 당사자 정보가 프롬프트에 포함되어야 환각을 막는다."""
    msgs = build_chat_messages(
        [{"role": "user", "content": "임차인이 누구야?"}], _CONTEXT
    )
    system = msgs[0]["content"]
    assert "박준혁" in system  # 임차인
    assert "김철수" in system  # 임대인
    assert "이영희" in system  # 중개사


def test_system_message_limits_scope():
    msgs = build_chat_messages([{"role": "user", "content": "hi"}], _CONTEXT)
    system = msgs[0]["content"]
    assert "리포트" in system
    assert "거절" in system or "범위" in system


def test_user_messages_appended_after_system():
    history = [
        {"role": "user", "content": "첫 질문"},
        {"role": "assistant", "content": "첫 답변"},
        {"role": "user", "content": "둘째 질문"},
    ]
    msgs = build_chat_messages(history, _CONTEXT)
    assert len(msgs) == 4
    assert msgs[1:] == history
