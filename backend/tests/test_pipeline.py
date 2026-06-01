import json

from app import pipeline, upstage, realprice, lawd, blacklist
from app.pipeline import InputFile
from app.scaffold import RISK_IDS


def _patch(monkeypatch, *, classify_map=None, default_doc="임대차계약서",
           text="계약 본문", summary=None, chat_json=None):
    classify_map = classify_map or {}
    summary = summary or {"type": "전세", "parties": "A,B", "deposit": "1억", "duration": "x"}
    if chat_json is None:
        chat_json = json.dumps({"assessments": {}, "finalComment": "총평"}, ensure_ascii=False)
    monkeypatch.setattr(upstage, "classify", lambda b, f: classify_map.get(f, default_doc))
    monkeypatch.setattr(upstage, "parse", lambda b, f: text)
    monkeypatch.setattr(upstage, "extract", lambda t: summary)
    monkeypatch.setattr(upstage, "chat", lambda m: chat_json)


def _files(*names, content_type="application/pdf"):
    return [InputFile(b"bytes", n, content_type) for n in names]


def test_happy_path_success(monkeypatch):
    _patch(monkeypatch)
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"
    assert len(resp.data.riskAssessments) == len(RISK_IDS)
    assert resp.data.providedDocuments == ["임대차계약서"]


def test_bundle_with_supporting_docs(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"})
    resp = pipeline.analyze(_files("c.pdf", "등기.pdf"))
    assert resp.status == "success"
    assert "등기부등본" in resp.data.providedDocuments


def test_no_contract_in_bundle(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"}, default_doc="등기부등본")
    resp = pipeline.analyze(_files("등기.pdf"))
    assert resp.status == "error"
    assert resp.error.code == "not_contract"


def test_too_many_files(monkeypatch):
    _patch(monkeypatch)
    resp = pipeline.analyze(_files(*[f"f{i}.pdf" for i in range(11)]))
    assert resp.status == "error"
    assert resp.error.code == "too_many_files"


def test_no_files():
    resp = pipeline.analyze([])
    assert resp.status == "error"
    assert resp.error.code == "no_files"


def test_empty_text_is_ocr_failed(monkeypatch):
    _patch(monkeypatch, text="   ")
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "error"
    assert resp.error.code == "ocr_failed"


def test_unsupported_format():
    resp = pipeline.analyze([InputFile(b"bytes", "c.txt", "text/plain")])
    assert resp.status == "error"
    assert resp.error.code == "unsupported_format"


def test_upstage_exception_is_analysis_failed(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.setattr(upstage, "chat", lambda m: (_ for _ in ()).throw(RuntimeError("boom")))
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "error"
    assert resp.error.code == "analysis_failed"


def test_bad_llm_json_is_analysis_failed(monkeypatch):
    _patch(monkeypatch, chat_json="not json at all")
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "error"
    assert resp.error.code == "analysis_failed"


def test_rate_limit_is_rate_limited(monkeypatch):
    _patch(monkeypatch)

    def raise_rate_limit(b, f):
        raise upstage.RateLimitExceeded()

    monkeypatch.setattr(upstage, "parse", raise_rate_limit)
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "error"
    assert resp.error.code == "rate_limited"


def _summary_with_property():
    return {
        "type": "전세", "parties": "A,B", "deposit": "9억 5,000만원", "duration": "x",
        "address": "서울특별시 종로구 청운동 1-1", "buildingName": "OO아파트",
        "exclusiveArea": "84.97", "propertyType": "아파트",
    }


def test_jeonse_ratio_override_applied(monkeypatch):
    _patch(monkeypatch, summary=_summary_with_property())
    monkeypatch.setattr(lawd, "code_of", lambda addr, table=None: "11110")
    monkeypatch.setattr(
        realprice, "estimate",
        lambda pt, cd, bn, area: {"price": 1_000_000_000, "sampleCount": 5, "samples": []},
    )
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"
    jeonse = next(a for a in resp.data.riskAssessments if a.id == "jeonse-price-ratio")
    assert jeonse.level == "높음"  # 9.5억/10억 = 95%
    assert resp.data.riskCounts.high >= 1


def test_jeonse_ratio_fallback_when_estimate_none(monkeypatch):
    _patch(monkeypatch, summary=_summary_with_property())
    monkeypatch.setattr(lawd, "code_of", lambda addr, table=None: "11110")
    monkeypatch.setattr(realprice, "estimate", lambda pt, cd, bn, area: None)
    resp = pipeline.analyze(_files("c.pdf"))
    jeonse = next(a for a in resp.data.riskAssessments if a.id == "jeonse-price-ratio")
    assert jeonse.level == "확인 필요"  # LLM 폴백 유지


def test_jeonse_ratio_exception_does_not_break(monkeypatch):
    _patch(monkeypatch, summary=_summary_with_property())
    monkeypatch.setattr(lawd, "code_of", lambda addr, table=None: "11110")

    def boom(*a, **k):
        raise RuntimeError("api down")

    monkeypatch.setattr(realprice, "estimate", boom)
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"  # 예외 흡수


def test_jeonse_ratio_skipped_when_no_address(monkeypatch):
    _patch(monkeypatch)  # 기본 summary (address 없음)
    called = {"n": 0}
    monkeypatch.setattr(realprice, "estimate", lambda *a, **k: called.__setitem__("n", called["n"] + 1) or None)
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"
    assert called["n"] == 0


def test_building_name_from_registry_by_suffix():
    text = "경기도 부천시 원미구 중동 1040 덕유마을주공3아파트 제237동 제12층 제1206호"
    assert pipeline._building_name_from_registry(text) == "덕유마을주공3아파트"


def test_building_name_from_registry_fallback_no_suffix():
    # 흔한 접미어가 없는 건물명은 '제N동' 앞 토큰으로 잡는다
    text = "서울특별시 강남구 역삼동 100 그린홈 제3동 제101호"
    assert pipeline._building_name_from_registry(text) == "그린홈"


def test_building_name_from_registry_none():
    assert pipeline._building_name_from_registry("아무 의미 없는 텍스트") == ""


def test_jeonse_result_injected_into_chat_prompt(monkeypatch):
    # 실거래가가 chat 호출 '전에' 조회되어 프롬프트에 사실로 주입되는지 검증한다
    _patch(monkeypatch, summary=_summary_with_property())
    monkeypatch.setattr(lawd, "code_of", lambda addr, table=None: "11110")
    monkeypatch.setattr(
        realprice, "estimate",
        lambda pt, cd, bn, area: {"price": 1_000_000_000, "sampleCount": 7, "samples": []},
    )
    captured = {}
    monkeypatch.setattr(
        upstage, "chat",
        lambda m: captured.__setitem__("msgs", m) or json.dumps({"assessments": {}, "finalComment": "x"}, ensure_ascii=False),
    )
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"
    user = captured["msgs"][1]["content"]
    assert "실거래가 자동조회 결과" in user  # chat 이전에 실거래가가 계산되어 주입됨


def test_jeonse_ratio_building_name_supplemented_from_registry(monkeypatch):
    # 계약서 buildingName='없음' 이어도 등기부등본에서 건물명을 보완해 실거래가를 조회하고 출처를 단다
    summary = _summary_with_property()
    summary["buildingName"] = "없음"
    captured = {}

    def fake_parse(b, f):
        return "경기도 부천시 원미구 중동 1040 덕유마을주공3아파트 제237동" if "등기" in f else "계약 본문"

    def fake_estimate(pt, cd, bn, area):
        captured["bn"] = bn
        return {"price": 425_000_000, "sampleCount": 19, "samples": []}

    monkeypatch.setattr(upstage, "classify", lambda b, f: "등기부등본" if "등기" in f else "임대차계약서")
    monkeypatch.setattr(upstage, "parse", fake_parse)
    monkeypatch.setattr(upstage, "extract", lambda t: summary)
    monkeypatch.setattr(upstage, "chat", lambda m: json.dumps({"assessments": {}, "finalComment": "x"}, ensure_ascii=False))
    monkeypatch.setattr(lawd, "code_of", lambda addr, table=None: "41192")
    monkeypatch.setattr(realprice, "estimate", fake_estimate)

    resp = pipeline.analyze(_files("c.pdf", "등기.pdf"))
    assert resp.status == "success"
    assert captured["bn"] == "덕유마을주공3아파트"  # 등기부에서 보완됨
    jeonse = next(a for a in resp.data.riskAssessments if a.id == "jeonse-price-ratio")
    assert jeonse.dataSource == "국토교통부 실거래가 19건 기준"


def _registry_owner_text():
    return (
        "【 갑    구 】 (소유권에 관한 사항)\n"
        "소유자 고웅주 930101-1234567\n"
        "서울특별시 서대문구 성산로 309-29, 401호 (연희동)"
    )


def _fake_match(monkeypatch):
    """등기부 소유자가 명단과 강하게 일치하도록 match를 패치."""
    monkeypatch.setattr(
        blacklist, "match",
        lambda name, birth, addr, snapshot=None: {
            "name": "고웅주", "age": 33, "address": "서울 서대문구 성산로 309-29",
            "depositDebt": "1,032,000,000", "baseDate": "2026-01-27",
        },
    )


def test_blacklist_override_applied(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"})
    monkeypatch.setattr(upstage, "parse",
                        lambda b, f: _registry_owner_text() if "등기" in f else "계약 본문")
    _fake_match(monkeypatch)
    resp = pipeline.analyze(_files("c.pdf", "등기.pdf"))
    assert resp.status == "success"
    landlord = next(a for a in resp.data.riskAssessments if a.id == "multi-home-landlord")
    assert landlord.level == "높음"
    assert landlord.dataSource is not None and "HUG" in landlord.dataSource


def test_blacklist_no_match_keeps_llm(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"})
    monkeypatch.setattr(upstage, "parse",
                        lambda b, f: _registry_owner_text() if "등기" in f else "계약 본문")
    monkeypatch.setattr(blacklist, "match", lambda *a, **k: None)
    resp = pipeline.analyze(_files("c.pdf", "등기.pdf"))
    landlord = next(a for a in resp.data.riskAssessments if a.id == "multi-home-landlord")
    assert landlord.level == "확인 필요"  # LLM 폴백 유지(빈 assessments → 기본값)


def test_blacklist_skipped_without_registry(monkeypatch):
    _patch(monkeypatch)  # 등기부 없음(계약서만)
    called = {"n": 0}
    monkeypatch.setattr(blacklist, "match",
                        lambda *a, **k: called.__setitem__("n", called["n"] + 1) or None)
    resp = pipeline.analyze(_files("c.pdf"))
    assert resp.status == "success"
    assert called["n"] == 0  # 등기부 없으면 match 호출 안 함


def test_blacklist_exception_does_not_break(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"})
    monkeypatch.setattr(upstage, "parse",
                        lambda b, f: _registry_owner_text() if "등기" in f else "계약 본문")

    def boom(*a, **k):
        raise RuntimeError("snapshot broken")

    monkeypatch.setattr(blacklist, "match", boom)
    resp = pipeline.analyze(_files("c.pdf", "등기.pdf"))
    assert resp.status == "success"  # 예외 흡수


def test_blacklist_match_injected_into_chat_prompt(monkeypatch):
    _patch(monkeypatch, classify_map={"등기.pdf": "등기부등본"})
    monkeypatch.setattr(upstage, "parse",
                        lambda b, f: _registry_owner_text() if "등기" in f else "계약 본문")
    _fake_match(monkeypatch)
    captured = {}
    monkeypatch.setattr(
        upstage, "chat",
        lambda m: captured.__setitem__("msgs", m) or json.dumps(
            {"assessments": {}, "finalComment": "x"}, ensure_ascii=False),
    )
    pipeline.analyze(_files("c.pdf", "등기.pdf"))
    assert "악성임대인 명단 대조 결과" in captured["msgs"][1]["content"]
