import json
import re

from app.schema import AnalysisData, RiskAssessment, RiskCounts
from app.scaffold import (
    RISK_SCAFFOLD, PUBLIC_DOCUMENT_CHECKS, STAGE_CHECKLISTS,
    QUESTIONS_BY_TARGET, CHECKLIST, QUESTIONS_TO_ASK,
    REALPRICE_CHECK_NAME, ANSIM_CHECK_RESOLVED,
)

_LEVEL_BUCKET = {
    "고위험": "high", "높음": "high",
    "주의": "medium", "보통": "medium",
    "낮음": "low",
    "확인 필요": "needCheck",
}

# 분류기 라벨 → 공적서류 점검 항목 이름. 이름이 다른 것만 보정한다(나머지는 동일).
_PROVIDED_TO_CHECK_NAME = {
    "미납국세열람내역": "미납 국세·지방세 열람",
    "중개대상물확인서": "중개대상물 확인·설명서",
}

_DEFAULT_LEVEL = "확인 필요"
_DEFAULT_STATUS = "외부 서류 확인 필요"
_DEFAULT_FINDING = "이 항목은 계약서만으로 판단하기 어려워 외부 서류 확인이 필요합니다."
_DEFAULT_ACTION = "관련 공적 서류를 발급해 확인하세요."

# LLM 이 enum 을 벗어난 값을 뱉을 수 있어 허용 집합으로 보정한다.
_VALID_LEVELS = set(_LEVEL_BUCKET)
_VALID_STATUSES = {
    "계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당",
}


def _coerce(value, allowed: set, default: str) -> str:
    return value if value in allowed else default


def is_contract(doc_type: str) -> bool:
    return "임대차" in doc_type or "전월세" in doc_type or "임대차계약서" in doc_type


def parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    # 코드펜스 제거
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # 직접 파싱 시도
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # LLM이 앞뒤에 텍스트를 붙인 경우 { } 블록만 추출
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"LLM 응답에서 JSON을 찾을 수 없습니다: {raw[:200]!r}")


def count_levels(assessments: list[dict]) -> dict:
    counts = {"high": 0, "medium": 0, "low": 0, "needCheck": 0}
    for a in assessments:
        bucket = _LEVEL_BUCKET.get(a["level"], "needCheck")
        counts[bucket] += 1
    return counts


# 공적서류 중요도를 연결된 위험 항목의 위험도(level)에 맞춰 동적으로 매긴다.
# 고위험/높음과 연결되면 '높음', 주의/보통/확인 필요면 '보통', 그 외(낮음·미매칭)는 '낮음'.
def _importance_for(related_ids: list[str], level_by_id: dict[str, str]) -> str:
    levels = [level_by_id.get(rid) for rid in related_ids]
    if any(lv in ("고위험", "높음") for lv in levels):
        return "높음"
    if any(lv in ("주의", "보통", "확인 필요") for lv in levels):
        return "보통"
    return "낮음"


def build_data(summary: dict, llm: dict, provided_documents: list[str],
               realprice_resolved: bool = False) -> AnalysisData:
    llm_assessments = llm.get("assessments", {})
    merged: list[dict] = []
    for scaf in RISK_SCAFFOLD:
        var = llm_assessments.get(scaf["id"], {})
        merged.append({
            "id": scaf["id"],
            "title": scaf["title"],
            "category": scaf["category"],
            "requiredDocuments": scaf["requiredDocuments"],
            "contractClues": scaf["contractClues"],
            "whyImportant": scaf["whyImportant"],
            "stages": scaf["stages"],
            "level": _coerce(var.get("level"), _VALID_LEVELS, _DEFAULT_LEVEL),
            "status": _coerce(var.get("status"), _VALID_STATUSES, _DEFAULT_STATUS),
            "currentFinding": var.get("currentFinding", _DEFAULT_FINDING),
            "action": var.get("action", _DEFAULT_ACTION),
            "questions": var.get("questions") or scaf["questions"],
        })

    counts = count_levels(merged)
    # 이미 업로드한 공적서류는 '추가로 확인해야 할 서류'에서 제외한다.
    provided_check_names = {_PROVIDED_TO_CHECK_NAME.get(d, d) for d in provided_documents}
    public_checks = [c for c in PUBLIC_DOCUMENT_CHECKS if c["name"] not in provided_check_names]
    # 전세가율을 실거래가로 자동 확인했으면 해당 항목을 안심전세 App(보증·사고이력) 중심으로 다듬는다.
    if realprice_resolved:
        public_checks = [
            ANSIM_CHECK_RESOLVED if c["name"] == REALPRICE_CHECK_NAME else c
            for c in public_checks
        ]
    # 중요도를 연결된 위험 항목의 위험도에 맞춰 다시 매긴다(원본 dict 보존을 위해 복사본 생성).
    level_by_id = {m["id"]: m["level"] for m in merged}
    public_checks = [
        {**c, "importance": _importance_for(c.get("relatedRiskIds", []), level_by_id)}
        for c in public_checks
    ]
    return AnalysisData(
        summary=summary,
        riskCounts=RiskCounts(**counts),
        riskAssessments=[RiskAssessment(**m) for m in merged],
        publicDocumentChecks=public_checks,
        stageChecklists=STAGE_CHECKLISTS,
        questionsByTarget=QUESTIONS_BY_TARGET,
        finalComment=llm.get("finalComment", ""),
        risks=[],
        checklist=CHECKLIST,
        questions_to_ask=QUESTIONS_TO_ASK,
        providedDocuments=provided_documents,
    )
