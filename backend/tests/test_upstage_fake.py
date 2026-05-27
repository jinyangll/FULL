import json
from app import upstage


def test_fake_mode_returns_canned(monkeypatch):
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "true")
    assert upstage.classify(b"x", "a.pdf") == "임대차계약서"
    assert "임대차" in upstage.parse(b"x", "a.pdf")
    summary = upstage.extract("계약서 텍스트")
    assert "deposit" in summary
    raw = upstage.chat([{"role": "user", "content": "hi"}])
    parsed = json.loads(raw)
    assert "assessments" in parsed and "finalComment" in parsed


def test_real_mode_requires_api_key(monkeypatch):
    """실제 모드에서 키가 없으면 네트워크 호출 전에 명확한 에러를 낸다."""
    import pytest
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "false")
    monkeypatch.delenv("UPSTAGE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="UPSTAGE_API_KEY"):
        upstage.classify(b"x", "a.pdf")
