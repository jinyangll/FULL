import os
from app import blacklist

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "khug_sample.html")


def _sample_html() -> str:
    with open(FIXTURE, encoding="utf-8") as f:
        return f.read()


def test_parse_blacklist_page_extracts_rows():
    rows = blacklist.parse_blacklist_page(_sample_html())
    assert len(rows) == 2
    first = rows[0]
    assert first["name"] == "고웅주"
    assert first["age"] == 33
    assert first["address"] == "서울 서대문구 성산로 309-29, 401호 (연희동)"
    assert first["deposit_debt"] == "1,032,000,000"
    assert first["base_date"] == "2026-01-27"
    # birth_year = 기준일 연도 - 나이
    assert first["birth_year"] == 2026 - 33
    second = rows[1]
    assert second["name"] == "김임대"
    assert second["age"] == 52
    assert second["birth_year"] == 2026 - 52


def test_last_page_num_reads_last_link():
    assert blacklist.last_page_num(_sample_html()) == 3


def test_parse_blacklist_page_empty_when_no_table():
    assert blacklist.parse_blacklist_page("<html><body>없음</body></html>") == []


def test_normalize_name_strips_spaces():
    assert blacklist._normalize_name(" 고 웅주 ") == "고웅주"


def test_birth_year_from_rrn_1900s():
    # 850101-1 → 1985
    assert blacklist._birth_year("850101-1") == 1985


def test_birth_year_from_rrn_2000s():
    # 030101-3 → 2003
    assert blacklist._birth_year("030101-3") == 2003


def test_birth_year_none_when_unparseable():
    assert blacklist._birth_year("") is None
    assert blacklist._birth_year(None) is None


def test_birth_year_matches_within_one():
    assert blacklist._birth_year_matches(1990, 1991) is True
    assert blacklist._birth_year_matches(1990, 1990) is True
    assert blacklist._birth_year_matches(1990, 1993) is False
    assert blacklist._birth_year_matches(None, 1990) is False


def test_address_matches_same_sigungu_and_road():
    owner = "서울특별시 서대문구 성산로 309-29 401호"
    listed = "서울 서대문구 성산로 309-29, 401호 (연희동)"
    assert blacklist._address_matches(owner, listed) is True


def test_address_no_match_different_district():
    assert blacklist._address_matches("서울 강남구 테헤란로 1", "서울 서대문구 성산로 309") is False


def test_looks_like_company():
    assert blacklist._looks_like_company("주식회사한빛") is True
    assert blacklist._looks_like_company("㈜대성") is True
    assert blacklist._looks_like_company("고웅주") is False


def test_match_name_and_birth_year():
    snap = [{"name": "고웅주", "birth_year": 1993, "age": 33,
             "address": "서울 서대문구 성산로 309-29", "deposit_debt": "1,032,000,000",
             "base_date": "2026-01-27"}]
    r = blacklist.match("고웅주", "930101-1", "부산 해운대구 우동 1", snap)
    assert r is not None
    assert r["name"] == "고웅주"
    assert r["depositDebt"] == "1,032,000,000"
    assert r["baseDate"] == "2026-01-27"


def test_match_name_and_address():
    snap = [{"name": "고웅주", "birth_year": 1993, "age": 33,
             "address": "서울 서대문구 성산로 309-29, 401호 (연희동)",
             "deposit_debt": "1,032,000,000", "base_date": "2026-01-27"}]
    # 생년 불일치(1980)지만 주소 일치 → 강한 일치
    r = blacklist.match("고웅주", "800101-1", "서울특별시 서대문구 성산로 309-29 401호", snap)
    assert r is not None


def test_match_name_only_is_none():
    # 동명이인: 이름만 같고 생년·주소 모두 불일치
    snap = [{"name": "고웅주", "birth_year": 1993, "age": 33,
             "address": "서울 서대문구 성산로 309-29", "deposit_debt": "1",
             "base_date": "2026-01-27"}]
    assert blacklist.match("고웅주", "800101-1", "부산 해운대구 우동 1", snap) is None


def test_match_no_name_match_is_none():
    snap = [{"name": "고웅주", "birth_year": 1993, "age": 33,
             "address": "서울 서대문구 성산로 309-29", "deposit_debt": "1",
             "base_date": "2026-01-27"}]
    assert blacklist.match("홍길동", "930101-1", "서울 서대문구 성산로 309-29", snap) is None


def test_match_company_owner_skipped():
    snap = [{"name": "주식회사고웅주", "birth_year": 0, "age": 0,
             "address": "서울 서대문구 성산로 309-29", "deposit_debt": "1",
             "base_date": "2026-01-27"}]
    assert blacklist.match("주식회사고웅주", None, "서울 서대문구 성산로 309-29", snap) is None


def test_match_uses_fake_snapshot_when_no_arg(monkeypatch):
    monkeypatch.setenv("USE_FAKE_BLACKLIST", "true")
    # 캔드 명단의 '홍길동'(1985, 서울 강남구 테헤란로)와 강하게 일치
    r = blacklist.match("홍길동", "850101-1", "서울특별시 강남구 테헤란로 152", None)
    assert r is not None
    assert r["name"] == "홍길동"


def test_owner_from_registry_extracts_fields():
    text = (
        "【 갑    구 】 (소유권에 관한 사항)\n"
        "2  소유권이전  2020년5월1일  매매\n"
        "소유자 고웅주 930101-1234567\n"
        "서울특별시 서대문구 성산로 309-29, 401호 (연희동)"
    )
    name, birth, addr = blacklist._owner_from_registry(text)
    assert name == "고웅주"
    assert birth.startswith("930101")
    assert "서대문구" in addr


def test_owner_from_registry_no_owner():
    assert blacklist._owner_from_registry("아무 의미 없는 텍스트") == ("", None, None)
