from app.prompt import build_messages
from app.scaffold import RISK_IDS


def test_messages_shape_and_content():
    msgs = build_messages("계약서 본문 텍스트", {"deposit": "1억원"})
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    joined = " ".join(m["content"] for m in msgs)
    for rid in RISK_IDS:
        assert rid in joined
    assert "계약서 본문 텍스트" in joined
    assert "1억원" in joined
    assert "JSON" in joined
