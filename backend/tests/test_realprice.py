from app import realprice


def test_parse_deposit_plain():
    assert realprice._parse_deposit("100,000,000원") == 100_000_000


def test_parse_deposit_eok_man():
    assert realprice._parse_deposit("1억 2,000만원") == 120_000_000


def test_parse_deposit_eok_only():
    assert realprice._parse_deposit("3억원") == 300_000_000


def test_parse_deposit_unparseable():
    assert realprice._parse_deposit("확인 필요") is None


def test_parse_area():
    assert realprice.parse_area("84.97") == 84.97
    assert realprice.parse_area("59.8㎡") == 59.8
    assert realprice.parse_area("확인 필요") is None


def _row(amount, area, name="OO아파트", ym="202604"):
    return {"amount": amount, "area": area, "name": name, "ym": ym}


def test_match_filters_by_area_tolerance():
    rows = [_row(80000, 84.0), _row(80000, 92.0), _row(80000, 100.0)]
    out = realprice._match(rows, "OO아파트", 84.97)
    assert len(out) == 2


def test_match_filters_by_building_name():
    rows = [_row(80000, 84.0, name="OO아파트"), _row(80000, 84.0, name="XX빌라")]
    out = realprice._match(rows, "OO아파트", 84.0)
    assert len(out) == 1


def test_match_skips_name_when_no_building():
    rows = [_row(80000, 84.0, name="아무거나")]
    out = realprice._match(rows, "", 84.0)
    assert len(out) == 1


def test_normalize_name_strips_parens_and_symbols():
    assert realprice._normalize_name("덕유마을(주공3)") == "덕유마을주공3"
    assert realprice._normalize_name("덕유마을주공3아파트") == "덕유마을주공3아파트"


def test_match_handles_registry_vs_molit_name_format():
    # 등기부등본 '덕유마을주공3아파트' 로 MOLIT '덕유마을(주공3)' 행을 매칭해야 한다(포맷 차이 흡수)
    rows = [_row(42500, 58.74, name="덕유마을(주공3)")]
    out = realprice._match(rows, "덕유마을주공3아파트", 58.74)
    assert len(out) == 1


def test_median_won_converts_manwon():
    rows = [_row(70000, 84.0), _row(80000, 84.0), _row(90000, 84.0)]
    assert realprice._median_won(rows) == 800_000_000


def test_fmt_won():
    assert realprice._fmt_won(800_000_000) == "8억원"
    assert realprice._fmt_won(820_000_000) == "8억 2,000만원"
    assert realprice._fmt_won(50_000_000) == "5,000만원"


_SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><body><items>
  <item>
    <aptNm>OO아파트</aptNm><dealAmount> 80,000</dealAmount>
    <excluUseAr>84.97</excluUseAr><dealYear>2026</dealYear>
    <dealMonth>4</dealMonth><dealDay>10</dealDay>
  </item>
  <item>
    <aptNm>OO아파트</aptNm><dealAmount> 82,500</dealAmount>
    <excluUseAr>84.97</excluUseAr><dealYear>2026</dealYear>
    <dealMonth>4</dealMonth><dealDay>15</dealDay>
  </item>
</items></body></response>"""


def test_norm_type():
    assert realprice._norm_type("아파트") == "아파트"
    assert realprice._norm_type("오피스텔") == "오피스텔"
    assert realprice._norm_type("빌라(연립다세대)") == "연립다세대"
    assert realprice._norm_type("다가구주택") == "단독다가구"
    assert realprice._norm_type("확인 필요") is None


def test_parse_items_apt():
    rows = realprice._parse_items(_SAMPLE_XML, "aptNm", "excluUseAr")
    assert len(rows) == 2
    assert rows[0]["amount"] == 80000
    assert rows[0]["area"] == 84.97
    assert rows[0]["name"] == "OO아파트"
    assert rows[0]["ym"] == "202604"


def _est(price, n=5):
    return {"price": price, "sampleCount": n, "samples": []}


def test_ratio_assessment_high():
    a = realprice.ratio_assessment("9억 5,000만원", _est(1_000_000_000))
    assert a["level"] == "높음"


def test_ratio_assessment_medium():
    a = realprice.ratio_assessment("8억 5,000만원", _est(1_000_000_000))
    assert a["level"] == "주의"


def test_ratio_assessment_low():
    a = realprice.ratio_assessment("6억원", _est(1_000_000_000))
    assert a["level"] == "낮음"


def test_ratio_assessment_status_and_finding():
    a = realprice.ratio_assessment("6억원", _est(1_000_000_000, n=4))
    assert a["status"] == "조건부 해당"
    assert "10억원" in a["currentFinding"]
    assert "4건" in a["currentFinding"]
    assert "60%" in a["currentFinding"]


def test_ratio_assessment_includes_data_source():
    a = realprice.ratio_assessment("6억원", _est(1_000_000_000, n=19))
    assert a["dataSource"] == "국토교통부 실거래가 19건 기준"


def test_ratio_assessment_unparseable_deposit():
    assert realprice.ratio_assessment("확인 필요", _est(1_000_000_000)) is None


def test_ratio_assessment_zero_price():
    assert realprice.ratio_assessment("3억원", {"price": 0, "sampleCount": 5, "samples": []}) is None


def test_estimate_fake_returns_canned(monkeypatch):
    monkeypatch.setenv("USE_FAKE_REALPRICE", "true")
    est = realprice.estimate("아파트", "11110", "OO아파트", 84.97)
    assert est is not None
    assert est["price"] > 0
    assert est["sampleCount"] >= 3


def test_estimate_unknown_type_returns_none(monkeypatch):
    monkeypatch.setenv("USE_FAKE_REALPRICE", "true")
    assert realprice.estimate("확인 필요", "11110", "OO", 84.97) is None


def test_estimate_real_insufficient_samples(monkeypatch):
    monkeypatch.setenv("USE_FAKE_REALPRICE", "false")
    monkeypatch.setattr(realprice, "_recent_months", lambda n=6: ["202604"])
    monkeypatch.setattr(
        realprice, "_fetch_month",
        lambda service, lawd_cd, ym: [
            {"amount": 80000, "area": 84.0, "name": "OO아파트", "ym": ym},
            {"amount": 81000, "area": 84.0, "name": "OO아파트", "ym": ym},
        ],
    )
    assert realprice.estimate("아파트", "11110", "OO아파트", 84.0) is None


def test_estimate_real_enough_samples(monkeypatch):
    monkeypatch.setenv("USE_FAKE_REALPRICE", "false")
    monkeypatch.setattr(realprice, "_recent_months", lambda n=6: ["202604"])
    monkeypatch.setattr(
        realprice, "_fetch_month",
        lambda service, lawd_cd, ym: [
            {"amount": 79000, "area": 84.0, "name": "OO아파트", "ym": ym},
            {"amount": 80000, "area": 84.0, "name": "OO아파트", "ym": ym},
            {"amount": 81000, "area": 84.0, "name": "OO아파트", "ym": ym},
        ],
    )
    est = realprice.estimate("아파트", "11110", "OO아파트", 84.0)
    assert est["price"] == 800_000_000
    assert est["sampleCount"] == 3
