from __future__ import annotations

import logging
from dataclasses import dataclass

from app import upstage, realprice, lawd, blacklist
from app.prompt import build_messages
from app.mapper import is_contract, parse_llm_json, build_data, count_levels
from app.schema import AnalysisResponse, ErrorInfo, RiskCounts

logger = logging.getLogger(__name__)

_ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}
_MAX_FILES = 10

_MESSAGES = {
    "no_files": "분석할 파일이 없습니다.",
    "too_many_files": f"한 번에 최대 {_MAX_FILES}개까지 업로드할 수 있습니다.",
    "not_contract": "임대차계약서로 보이는 문서가 없습니다.",
    "ocr_failed": "문서에서 텍스트를 추출하지 못했습니다.",
    "unsupported_format": "PDF, JPG, PNG 형식만 지원합니다.",
    "rate_limited": "현재 분석 요청이 많아 처리가 지연되고 있습니다. 잠시 후 다시 시도해 주세요.",
    "analysis_failed": "분석 중 오류가 발생했습니다.",
}


@dataclass
class InputFile:
    file_bytes: bytes
    filename: str
    content_type: str


def _error(code: str) -> AnalysisResponse:
    return AnalysisResponse(status="error", error=ErrorInfo(code=code, message=_MESSAGES[code]))


def analyze(files: list[InputFile]) -> AnalysisResponse:
    if not files:
        return _error("no_files")
    if len(files) > _MAX_FILES:
        return _error("too_many_files")
    for f in files:
        if f.content_type not in _ALLOWED_TYPES:
            return _error("unsupported_format")
    try:
        # 분류는 저렴하므로 먼저 전부 수행하고, OCR(parse)은 계약서 확정 후 필요한 것만 호출한다.
        doc_types = [upstage.classify(f.file_bytes, f.filename) for f in files]

        contract_idx = next(
            (i for i, dt in enumerate(doc_types) if is_contract(dt)), None
        )
        if contract_idx is None:
            return _error("not_contract")
        contract_text = upstage.parse(
            files[contract_idx].file_bytes, files[contract_idx].filename
        )
        if not contract_text or not contract_text.strip():
            return _error("ocr_failed")

        supporting = []  # list[(doc_type, text)]
        for i, (f, dt) in enumerate(zip(files, doc_types)):
            if i == contract_idx or dt == "기타" or is_contract(dt):
                continue
            text = upstage.parse(f.file_bytes, f.filename)
            if text and text.strip():
                supporting.append((dt, text))

        summary = upstage.extract(contract_text)
        # 실거래가를 chat 이전에 조회해, 그 결과를 LLM 프롬프트에 확정 사실로 주입한다.
        # (총평이 전세가율 판정과 모순되지 않도록. 추가 LLM 호출은 없고 순서만 바꾼다.)
        jeonse = compute_jeonse_ratio(summary, supporting)
        landlord = compute_blacklist_match(supporting)
        messages = build_messages(contract_text, summary, supporting, jeonse, landlord)
        raw = upstage.chat(messages)
        llm = parse_llm_json(raw)
        provided = ["임대차계약서"] + [dt for dt, _ in supporting]
        data = build_data(summary, llm, provided, realprice_resolved=jeonse is not None)
        if jeonse is not None:
            _apply_jeonse_ratio(data, jeonse)
        if landlord is not None:
            _apply_blacklist_match(data, landlord)
        return AnalysisResponse(status="success", data=data)
    except upstage.RateLimitExceeded:
        logger.warning("analyze() rate limit(429)")
        return _error("rate_limited")
    except Exception:
        logger.exception("analyze() 실패")
        return _error("analysis_failed")


# 등기부등본·계약서에 나타나는 흔한 건물 유형 접미어
_BUILDING_SUFFIX = "아파트|오피스텔|빌라|연립|맨션|타운|하이츠|팰리스|캐슬|파크|시티|힐스"
_PLACEHOLDER_NAMES = ("없음", "확인 필요", "미확인", "N/A")


def _building_name_from_registry(text: str) -> str:
    """등기부등본(집합건물) 표제부 텍스트에서 건물명을 추출한다.
    1) 흔한 유형 접미어로 끝나는 명칭, 2) '제N동' 앞 토큰을 폴백으로 사용."""
    import re
    m = re.search(rf"([가-힣A-Za-z0-9()]+(?:{_BUILDING_SUFFIX}))", text)
    if m:
        return m.group(1)
    # 지번 다음 '제N동' 앞 명칭 (예: '1040 덕유마을주공3아파트 제237동')
    m = re.search(r"\d+\s+([가-힣A-Za-z0-9()]+?)\s+제?\s*\d+동", text)
    return m.group(1) if m else ""


def compute_jeonse_ratio(summary: dict, supporting: list | None = None) -> dict | None:
    """실거래가 시세 기반 전세가율 판정을 계산한다(부수효과 없음).
    성공 시 override dict(level/status/currentFinding/action/dataSource), 실패 시 None.
    어떤 실패도 분석을 막지 않는다(예외 흡수). 각 스킵 지점은 info 로그로 남긴다."""
    try:
        ptype = summary.get("propertyType")
        address = summary.get("address")
        area_raw = summary.get("exclusiveArea")
        if not ptype or not address or not area_raw:
            logger.info("전세가율 스킵: 필수 필드 누락 (유형=%r 주소=%r 면적=%r)", ptype, address, area_raw)
            return None
        # extract가 값을 못 찾으면 "확인 필요" 같은 문구를 채워 넣으므로, 그 경우는 자동판정을 건너뛴다.
        if "확인" in str(ptype) or "확인" in str(area_raw):
            logger.info("전세가율 스킵: 유형/면적 미확정 (유형=%r 면적=%r)", ptype, area_raw)
            return None
        area = realprice.parse_area(area_raw)
        if area is None:
            logger.info("전세가율 스킵: 면적 파싱 실패 (%r)", area_raw)
            return None
        lawd_cd = lawd.code_of(address)
        if lawd_cd is None:
            logger.info("전세가율 스킵: 법정동코드 매칭 실패 (주소=%r)", address)
            return None
        building_name = summary.get("buildingName") or ""
        if building_name in _PLACEHOLDER_NAMES:
            building_name = ""
        if not building_name and supporting:
            for dt, text in supporting:
                if dt == "등기부등본":
                    building_name = _building_name_from_registry(text)
                    if building_name:
                        logger.info("건물명 보완: 등기부등본에서 %r 추출", building_name)
                        break
        if not building_name:
            logger.info("전세가율 진행(주의): 건물명 미확보 → 단지 특정 없이 조회")
        est = realprice.estimate(ptype, lawd_cd, building_name, area)
        if est is None:
            logger.info("전세가율 스킵: 실거래가 추정 불가 (유형=%r 코드=%s 건물명=%r)", ptype, lawd_cd, building_name)
            return None
        override = realprice.ratio_assessment(summary.get("deposit", ""), est)
        if override is None:
            logger.info("전세가율 스킵: 보증금 파싱 실패 (%r)", summary.get("deposit"))
            return None
        logger.info("전세가율 자동판정 성공: %s (%s)", override["level"], override["dataSource"])
        return override
    except Exception:
        logger.exception("전세가율 자동판정 실패(무시)")
        return None


def _apply_jeonse_ratio(data, override: dict) -> None:
    """미리 계산한 override 를 jeonse-price-ratio 항목에 기록하고 위험 카운트를 갱신한다."""
    for a in data.riskAssessments:
        if a.id == "jeonse-price-ratio":
            a.level = override["level"]
            a.status = override["status"]
            a.currentFinding = override["currentFinding"]
            a.action = override["action"]
            a.dataSource = override["dataSource"]
            break
    counts = count_levels([{"level": a.level} for a in data.riskAssessments])
    data.riskCounts = RiskCounts(**counts)


def compute_blacklist_match(supporting: list | None = None) -> dict | None:
    """등기부 소유자를 HUG 상습채무불이행자 명단과 대조해 multi-home-landlord override 를 만든다.
    강한 일치 시에만 override dict, 아니면 None. 어떤 실패도 분석을 막지 않는다(예외 흡수)."""
    try:
        if not supporting:
            return None
        registry = next((text for dt, text in supporting if dt == "등기부등본"), None)
        if not registry:
            logger.info("악성임대인 대조 스킵: 등기부등본 미제출")
            return None
        name, birth, addr = blacklist._owner_from_registry(registry)
        if not name:
            logger.info("악성임대인 대조 스킵: 등기부에서 소유자 성명 추출 실패")
            return None
        hit = blacklist.match(name, birth, addr)
        if hit is None:
            return None
        age_txt = f"만 {hit['age']}세, " if hit.get("age") else ""
        finding = (
            f"등기부 소유자 {hit['name']}({age_txt}{hit['address']})이 "
            f"HUG 상습채무불이행자 공개 명단의 인적사항과 일치합니다. "
            f"반환채무 약 {hit['depositDebt']}원(기준일 {hit['baseDate']}). "
            f"이는 단정이 아니며, 안심전세포털에서 직접 최종 확인하세요."
        )
        logger.info("악성임대인 명단 일치: %s (기준일 %s)", hit["name"], hit["baseDate"])
        return {
            "level": "높음",
            "status": "외부 서류 확인 필요",
            "currentFinding": finding,
            "action": "안심전세포털 상습채무불이행자 명단에서 성명·생년·주소를 직접 대조하고, 계약 전 임대인에게 소명을 요청하세요.",
            "dataSource": f"HUG 상습채무불이행자 명단(기준일 {hit['baseDate']}) 대조",
        }
    except Exception:
        logger.exception("악성임대인 대조 실패(무시)")
        return None


def _apply_blacklist_match(data, override: dict) -> None:
    """미리 계산한 override 를 multi-home-landlord 항목에 기록하고 위험 카운트를 갱신한다."""
    for a in data.riskAssessments:
        if a.id == "multi-home-landlord":
            a.level = override["level"]
            a.status = override["status"]
            a.currentFinding = override["currentFinding"]
            a.action = override["action"]
            a.dataSource = override["dataSource"]
            break
    counts = count_levels([{"level": a.level} for a in data.riskAssessments])
    data.riskCounts = RiskCounts(**counts)
