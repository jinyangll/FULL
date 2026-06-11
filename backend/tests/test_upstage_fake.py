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


def test_fake_classify_uses_filename_keyword(monkeypatch):
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "true")
    from app import upstage
    assert upstage.classify(b"x", "등기부등본.pdf") == "등기부등본"
    assert upstage.classify(b"x", "건축물대장.pdf") == "건축물대장"
    assert upstage.classify(b"x", "내계약서.pdf") == "임대차계약서"


class _Resp:
    def __init__(self, status_code):
        self.status_code = status_code


def test_is_rate_limit_detects_429():
    assert upstage._is_rate_limit(Exception()) is False
    err_with_resp = Exception()
    err_with_resp.response = _Resp(429)
    assert upstage._is_rate_limit(err_with_resp) is True
    err_with_status = Exception()
    err_with_status.status_code = 429
    assert upstage._is_rate_limit(err_with_status) is True
    err_500 = Exception()
    err_500.response = _Resp(500)
    assert upstage._is_rate_limit(err_500) is False


def _make_429():
    err = Exception("rate limited")
    err.status_code = 429
    return err


def test_with_retry_raises_rate_limit_exceeded(monkeypatch):
    import pytest
    monkeypatch.setattr(upstage.time, "sleep", lambda s: None)

    def always_429():
        raise _make_429()

    with pytest.raises(upstage.RateLimitExceeded):
        upstage._with_retry(always_429)


def test_with_retry_succeeds_after_transient_429(monkeypatch):
    monkeypatch.setattr(upstage.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise _make_429()
        return "ok"

    assert upstage._with_retry(flaky) == "ok"
    assert calls["n"] == 2


def test_with_retry_reraises_non_rate_limit(monkeypatch):
    import pytest
    monkeypatch.setattr(upstage.time, "sleep", lambda s: None)

    def boom():
        raise ValueError("other error")

    with pytest.raises(ValueError, match="other error"):
        upstage._with_retry(boom)


def test_fake_summary_has_realprice_fields(monkeypatch):
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "true")
    summary = upstage.extract("계약서 텍스트")
    for key in ("address", "buildingName", "exclusiveArea", "propertyType"):
        assert key in summary


def test_converse_fake_returns_string(monkeypatch):
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "true")
    reply = upstage.converse([{"role": "user", "content": "가장 위험한 항목이 뭐예요?"}])
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_converse_real_requires_api_key(monkeypatch):
    import pytest
    monkeypatch.setenv("USE_FAKE_UPSTAGE", "false")
    monkeypatch.delenv("UPSTAGE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="UPSTAGE_API_KEY"):
        upstage.converse([{"role": "user", "content": "hi"}])
