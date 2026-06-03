"""국토교통부 실거래가 API 연동 + 전세가율 판정.

USE_FAKE_REALPRICE=true 면 캔드 시세를 반환한다(키 없이 개발/테스트).
"""
from __future__ import annotations

import logging
import os
import re
import statistics
from datetime import date
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def _fake() -> bool:
    return os.getenv("USE_FAKE_REALPRICE", "false").lower() == "true"


def _parse_deposit(text: str) -> int | None:
    """'100,000,000원', '1억 2,000만원', '3억원' 등을 원 단위 정수로."""
    if not text:
        return None
    s = text.replace(",", "").replace(" ", "")
    m = re.search(r"(\d+)억(?:(\d+)만)?", s)
    if m:
        eok = int(m.group(1))
        man = int(m.group(2)) if m.group(2) else 0
        return eok * 10**8 + man * 10**4
    m = re.search(r"(\d+)만원", s)
    if m:
        return int(m.group(1)) * 10**4
    digits = re.sub(r"[^\d]", "", s)
    if digits:
        return int(digits)
    return None


def parse_area(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"\d+(?:\.\d+)?", str(text))
    return float(m.group()) if m else None


def _normalize_name(s: str) -> str:
    """괄호·특수문자 제거 후 한글·영숫자만 남긴다. MOLIT명 vs 등기부등본명 포맷 차이를 흡수."""
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", s)


def _match(rows: list[dict], building_name: str, area: float) -> list[dict]:
    """전용면적 ±10% & (건물명 부분일치 또는 건물명 없음) 행만 남긴다."""
    bn = _normalize_name(building_name or "")
    out = []
    for r in rows:
        a = r.get("area") or 0
        if a <= 0 or abs(a - area) / area > 0.10:
            continue
        rname = _normalize_name(r.get("name") or "")
        if bn and rname and bn not in rname and rname not in bn:
            continue
        out.append(r)
    return out


def _median_won(rows: list[dict]) -> int:
    """거래금액(만원) 중앙값을 원 단위 정수로 반환."""
    # MOLIT dealAmount 는 만원 단위라는 가정에 의존한다(×10**4 로 원 변환).
    median_manwon = statistics.median(r["amount"] for r in rows)
    return int(round(median_manwon)) * 10**4


def _fmt_won(won: int) -> str:
    eok = won // 10**8
    man = (won % 10**8) // 10**4
    if eok and man:
        return f"{eok}억 {man:,}만원"
    if eok:
        return f"{eok}억원"
    return f"{man:,}만원"


# 유형 → (서비스명, 건물명 태그, 면적 태그). operation = "get"+서비스명.
_SERVICE = {
    "아파트":     ("RTMSDataSvcAptTradeDev", "aptNm",    "excluUseAr"),
    "연립다세대": ("RTMSDataSvcRHTrade",     "mhouseNm", "excluUseAr"),
    "단독다가구": ("RTMSDataSvcSHTrade",     None,       "totalFloorAr"),
    "오피스텔":   ("RTMSDataSvcOffiTrade",   "offiNm",   "excluUseAr"),
}


def _norm_type(s: str) -> str | None:
    s = s or ""
    if "아파트" in s:
        return "아파트"
    if "오피스텔" in s:
        return "오피스텔"
    if "연립" in s or "다세대" in s or "빌라" in s:
        return "연립다세대"
    if "단독" in s or "다가구" in s:
        return "단독다가구"
    return None


def _text(item, tag) -> str:
    el = item.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def _parse_items(xml_text: str, name_tag: str | None, area_tag: str) -> list[dict]:
    """실거래가 XML 응답에서 거래 행 리스트를 추출한다."""
    rows = []
    root = ET.fromstring(xml_text)
    for item in root.iter("item"):
        amount_raw = _text(item, "dealAmount").replace(",", "").replace(" ", "")
        area_raw = _text(item, area_tag)
        if not amount_raw or not area_raw:
            continue
        try:
            amount = int(amount_raw)
            area = float(area_raw)
        except ValueError:
            continue
        year = _text(item, "dealYear")
        month = _text(item, "dealMonth").zfill(2)
        name = _text(item, name_tag) if name_tag else ""
        rows.append({"amount": amount, "area": area, "name": name, "ym": f"{year}{month}"})
    return rows


def ratio_assessment(deposit_text: str, est: dict) -> dict | None:
    """전세가율을 계산해 jeonse-price-ratio override 필드를 만든다.
    보증금 파싱 실패 시 None."""
    deposit = _parse_deposit(deposit_text)
    if deposit is None:
        return None
    price = est["price"]
    if not price:
        return None
    ratio = deposit / price
    pct = round(ratio * 100)
    if ratio >= 0.90:
        level = "높음"
        action = "전세가율이 매우 높아 깡통전세 위험이 있습니다. 보증보험 가입 가능 여부를 반드시 확인하고 계약 진행을 신중히 결정하세요."
    elif ratio >= 0.80:
        level = "주의"
        action = "전세가율이 다소 높습니다. 보증보험 가입 가능 여부와 시세 추가 근거를 확인하세요."
    else:
        level = "낮음"
        action = "전세가율은 안전 범위로 보이나, 잔금 전 시세·권리관계를 재확인하세요."
    finding = (
        f"최근 6개월 매매 실거래가 중앙값 {_fmt_won(price)}"
        f"(표본 {est['sampleCount']}건) 대비 보증금이 약 {pct}%입니다."
    )
    return {
        "level": level,
        "status": "조건부 해당",
        "currentFinding": finding,
        "action": action,
        "dataSource": f"국토교통부 실거래가 {est['sampleCount']}건 기준",
    }


_MIN_SAMPLES = 3
_DATA_GO_KR_BASE = "https://apis.data.go.kr/1613000"
_cache: dict[tuple, list[dict]] = {}


def _recent_months(n: int = 6) -> list[str]:
    """오늘 기준 최근 n개월의 YYYYMM 리스트."""
    today = date.today()
    months = []
    y, m = today.year, today.month
    for _ in range(n):
        months.append(f"{y}{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return months


def _data_go_kr_key() -> str:
    key = os.getenv("DATA_GO_KR_KEY")
    if not key:
        raise RuntimeError("DATA_GO_KR_KEY 가 설정되지 않았습니다 (backend/.env 확인).")
    return key


def _service_type(service: str) -> str:
    for ptype, (svc, _, _) in _SERVICE.items():
        if svc == service:
            return ptype
    raise KeyError(service)


def _fetch_month(service: str, lawd_cd: str, ym: str) -> list[dict]:
    """한 달치 매매 실거래가를 조회·파싱한다. (service, lawd_cd, ym) 단위 캐시."""
    cache_key = (service, lawd_cd, ym)
    if cache_key in _cache:
        return _cache[cache_key]
    import requests
    ptype = _service_type(service)
    _, name_tag, area_tag = _SERVICE[ptype]
    url = f"{_DATA_GO_KR_BASE}/{service}/get{service}"
    resp = requests.get(
        url,
        params={
            "serviceKey": _data_go_kr_key(),
            "LAWD_CD": lawd_cd,
            "DEAL_YMD": ym,
            "numOfRows": 1000,
            "pageNo": 1,
        },
        timeout=20,
    )
    resp.raise_for_status()
    rows = _parse_items(resp.text, name_tag, area_tag)
    _cache[cache_key] = rows
    return rows


def estimate(property_type: str, lawd_cd: str, building_name: str,
             exclusive_area: float) -> dict | None:
    """매매 실거래가 시세를 추정한다. 표본 부족/조회 실패 시 None."""
    ptype = _norm_type(property_type)
    if ptype is None:
        logger.info("실거래가 추정 스킵: 지원하지 않는 주택유형 %r", property_type)
        return None
    if _fake():
        samples = [{"amount": 80000, "area": exclusive_area, "name": building_name, "ym": "202604"}] * 5
        return {"price": 800_000_000, "sampleCount": 5, "samples": samples}
    service = _SERVICE[ptype][0]
    matched: list[dict] = []
    try:
        for ym in _recent_months(6):
            rows = _fetch_month(service, lawd_cd, ym)
            matched.extend(_match(rows, building_name, exclusive_area))
    except Exception:
        logger.exception("실거래가 조회 실패")
        return None
    if len(matched) < _MIN_SAMPLES:
        logger.info(
            "실거래가 표본 부족: %s %s 건물명=%r 면적=%.1f → 매칭 %d건(<%d)",
            ptype, lawd_cd, building_name, exclusive_area, len(matched), _MIN_SAMPLES,
        )
        return None
    return {"price": _median_won(matched), "sampleCount": len(matched), "samples": matched}
