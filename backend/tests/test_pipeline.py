from app import pipeline, upstage
from app.scaffold import RISK_IDS


def _patch(monkeypatch, *, doc="임대차계약서", text="계약 본문",
           summary=None, chat_json=None):
    import json
    summary = summary or {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    if chat_json is None:
        chat_json = json.dumps({"assessments": {}, "finalComment": "총평"}, ensure_ascii=False)
    monkeypatch.setattr(upstage, "classify", lambda b, f: doc)
    monkeypatch.setattr(upstage, "parse", lambda b, f: text)
    monkeypatch.setattr(upstage, "extract", lambda t: summary)
    monkeypatch.setattr(upstage, "chat", lambda m: chat_json)


def test_happy_path_success(monkeypatch):
    _patch(monkeypatch)
    resp = pipeline.analyze(b"bytes", "c.pdf", "application/pdf")
    assert resp.status == "success"
    assert len(resp.data.riskAssessments) == len(RISK_IDS)


def test_not_a_contract(monkeypatch):
    _patch(monkeypatch, doc="졸업증명서")
    resp = pipeline.analyze(b"bytes", "c.pdf", "application/pdf")
    assert resp.status == "error"
    assert resp.error.code == "not_contract"


def test_empty_text_is_ocr_failed(monkeypatch):
    _patch(monkeypatch, text="   ")
    resp = pipeline.analyze(b"bytes", "c.pdf", "application/pdf")
    assert resp.status == "error"
    assert resp.error.code == "ocr_failed"


def test_unsupported_format():
    resp = pipeline.analyze(b"bytes", "c.txt", "text/plain")
    assert resp.status == "error"
    assert resp.error.code == "unsupported_format"


def test_upstage_exception_is_analysis_failed(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.setattr(upstage, "chat", lambda m: (_ for _ in ()).throw(RuntimeError("boom")))
    resp = pipeline.analyze(b"bytes", "c.pdf", "application/pdf")
    assert resp.status == "error"
    assert resp.error.code == "analysis_failed"


def test_bad_llm_json_is_analysis_failed(monkeypatch):
    _patch(monkeypatch, chat_json="not json at all")
    resp = pipeline.analyze(b"bytes", "c.pdf", "application/pdf")
    assert resp.status == "error"
    assert resp.error.code == "analysis_failed"
