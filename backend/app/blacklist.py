"""HUG 상습채무불이행자(악성임대인) 공개 명단 대조.

USE_FAKE_BLACKLIST=true 면 캔드 명단을 사용한다(스냅샷 파일 없이 개발/테스트).
순수 파싱/대조 로직만 두고, 명단 수집은 scripts/crawl_blacklist.py 가 담당한다.
"""
from __future__ import annotations
import csv
import logging
import os
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 데이터 행 셀 순서(성명,나이,주소,임차보증금반환채무,이행기,채무불이행기간,보증채무이행일,구상채무,강제집행횟수,기준일)
_NAME, _AGE, _ADDR, _DEBT, _BASE = 0, 1, 2, 3, 9


def parse_blacklist_page(html: str) -> list[dict]:
    """KHUG 명단 한 페이지 HTML에서 행 리스트를 추출한다. 테이블이 없으면 빈 리스트."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return []
    rows = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 10:
            continue
        cells = [td.get_text(strip=True) for td in tds]
        try:
            age = int(re.sub(r"[^\d]", "", cells[_AGE]) or 0)
        except ValueError:
            age = 0
        base_date = cells[_BASE]
        base_year = int(base_date[:4]) if base_date[:4].isdigit() else 0
        rows.append({
            "name": cells[_NAME],
            "age": age,
            "address": cells[_ADDR],
            "deposit_debt": cells[_DEBT],
            "base_date": base_date,
            # 나이는 '기준일' 시점 기준이므로 출생연도 = 기준일 연도 - 나이.
            # (오늘 연도가 아니라 base_date 연도를 써야 기준일이 과거여도 정확하다.)
            "birth_year": base_year - age if base_year and age else 0,
        })
    return rows


def last_page_num(html: str) -> int:
    """페이지네이션에서 마지막 페이지 번호를 읽는다. 못 찾으면 1."""
    nums = [int(m) for m in re.findall(r"cur_page=(\d+)", html)]
    return max(nums) if nums else 1


_COMPANY_TOKENS = ("주식회사", "유한회사", "유한책임회사", "합자회사", "㈜", "(주)", "법인")


def _normalize_name(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def _looks_like_company(name: str) -> bool:
    n = name or ""
    return any(tok in n for tok in _COMPANY_TOKENS)


def _birth_year(rrn: str | None) -> int | None:
    """주민번호 앞 6자리(+성별코드)에서 출생연도(4자리)를 계산한다. 실패 시 None."""
    if not rrn:
        return None
    digits = re.sub(r"\D", "", rrn)
    if len(digits) < 6:
        return None
    yy = int(digits[:2])
    gender = digits[6] if len(digits) >= 7 else None
    if gender in ("1", "2", "5", "6"):
        century = 1900
    elif gender in ("3", "4", "7", "8"):
        century = 2000
    else:
        # 성별코드가 없으면: 성인 임대인 가정상 25 초과면 1900년대로 본다(휴리스틱).
        century = 1900 if yy > 25 else 2000
    return century + yy


def _birth_year_matches(owner_year: int | None, listed_year: int | None) -> bool:
    """출생연도 ±1 일치(기준일·계산 시점 차이를 흡수)."""
    if not owner_year or not listed_year:
        return False
    return abs(owner_year - listed_year) <= 1


def _address_tokens(addr: str) -> set[str]:
    """주소에서 시군구·도로명 등 의미 토큰만 추린다(시도 접미어·번지·괄호 제거)."""
    cleaned = re.sub(r"[(),]", " ", addr or "")
    out = set()
    for tok in cleaned.split():
        t = re.sub(r"(특별시|광역시|특별자치시|특별자치도|도|시)$", "", tok)
        t = re.sub(r"\d.*$", "", t)  # '309-29', '401호' 등 숫자 이후 제거
        if len(t) >= 2:
            out.add(t)
    return out


def _address_matches(owner_addr: str | None, listed_addr: str | None) -> bool:
    """시군구+도로명 토큰이 2개 이상 겹치면 동일 주소로 본다(호수 일치 불필요)."""
    if not owner_addr or not listed_addr:
        return False
    common = _address_tokens(owner_addr) & _address_tokens(listed_addr)
    return len(common) >= 2


_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "blacklist.csv")
_SNAPSHOT: list[dict] | None = None

# USE_FAKE_BLACKLIST=true 일 때 쓰는 캔드 명단(키 없이 개발/테스트).
_FAKE_SNAPSHOT: list[dict] = [
    {"name": "홍길동", "birth_year": 1985, "age": 41,
     "address": "서울특별시 강남구 테헤란로 152", "deposit_debt": "300,000,000",
     "base_date": "2026-01-27"},
]


def _fake() -> bool:
    return os.getenv("USE_FAKE_BLACKLIST", "false").lower() == "true"


def _load_snapshot() -> list[dict]:
    """로컬 스냅샷 CSV 로드(캐시). fake 모드면 캔드 명단. 파일 없으면 빈 리스트."""
    global _SNAPSHOT
    if _fake():
        return _FAKE_SNAPSHOT
    if _SNAPSHOT is not None:
        return _SNAPSHOT
    if not os.path.exists(_CSV_PATH):
        logger.info("악성임대인 스냅샷 없음: %s (대조 생략)", _CSV_PATH)
        _SNAPSHOT = []
        return _SNAPSHOT
    rows = []
    with open(_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({
                "name": row.get("name", ""),
                "birth_year": int(row["birth_year"]) if row.get("birth_year", "").isdigit() else 0,
                "age": int(row["age"]) if row.get("age", "").isdigit() else 0,
                "address": row.get("address", ""),
                "deposit_debt": row.get("deposit_debt", ""),
                "base_date": row.get("base_date", ""),
            })
    _SNAPSHOT = rows
    return _SNAPSHOT


def match(owner_name: str, owner_birth: str | None, owner_address: str | None,
          snapshot: list[dict] | None = None) -> dict | None:
    """소유자 신원을 명단과 강한 식별자로 대조. 강한 일치 시에만 dict, 아니면 None.

    강한 일치 = 성명 정규화 일치(필수) + (생년 ±1 일치 또는 주소 부분일치) 중 1개 이상.
    개인만 대상이므로 법인명으로 보이면 대조하지 않는다.
    """
    if not owner_name or _looks_like_company(owner_name):
        return None
    rows = snapshot if snapshot is not None else _load_snapshot()
    owner_year = _birth_year(owner_birth)
    target = _normalize_name(owner_name)
    for row in rows:
        if _normalize_name(row.get("name", "")) != target:
            continue
        if _looks_like_company(row.get("name", "")):
            continue
        strong = (
            _birth_year_matches(owner_year, row.get("birth_year"))
            or _address_matches(owner_address, row.get("address"))
        )
        if strong:
            return {
                "name": row.get("name", ""),
                "age": row.get("age") or None,
                "address": row.get("address", ""),
                "depositDebt": row.get("deposit_debt", ""),
                "baseDate": row.get("base_date", ""),
            }
    return None


# 등기부 주소 시작 토큰(시/도)
_SIDO = (
    "서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충청북도|충청남도|충북|충남|"
    "전라북도|전라남도|전북|전남|경상북도|경상남도|경북|경남|제주"
)


def _owner_from_registry(text: str) -> tuple[str, str | None, str | None]:
    """등기부등본 갑구 텍스트에서 (소유자 성명, 주민번호앞자리, 주소)를 추출한다.
    추출 실패 항목은 None. 성명조차 없으면 ("", None, None).
    (OCR 텍스트 변동을 고려한 휴리스틱 정규식)"""
    if not text:
        return ("", None, None)
    m = re.search(r"소유자\s*([가-힣]{2,4})\s*\(?\s*(\d{6})\s*[-–]?\s*(\d)?", text)
    if not m:
        return ("", None, None)
    name = m.group(1)
    birth = m.group(2) + ("-" + m.group(3) if m.group(3) else "")
    addr_m = re.search(rf"((?:{_SIDO})[^\n]{{2,60}})", text)
    address = addr_m.group(1).strip() if addr_m else None
    return (name, birth, address)
