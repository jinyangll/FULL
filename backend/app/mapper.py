import json
import re

from app.schema import AnalysisData, RiskAssessment, RiskCounts
from app.scaffold import (
    RISK_SCAFFOLD, PUBLIC_DOCUMENT_CHECKS, STAGE_CHECKLISTS,
    QUESTIONS_BY_TARGET, CHECKLIST, QUESTIONS_TO_ASK,
)

_LEVEL_BUCKET = {
    "고위험": "high", "높음": "high",
    "주의": "medium", "보통": "medium",
    "낮음": "low",
    "확인 필요": "needCheck",
    "판단 불가": "unknown",
}

_DEFAULT_LEVEL = "확인 필요"
_DEFAULT_STATUS = "외부 서류 확인 필요"
_DEFAULT_FINDING = "이 항목은 계약서만으로 판단하기 어려워 외부 서류 확인이 필요합니다."
_DEFAULT_ACTION = "관련 공적 서류를 발급해 확인하세요."

# LLM 이 enum 을 벗어난 값을 뱉을 수 있어 허용 집합으로 보정한다.
_VALID_LEVELS = set(_LEVEL_BUCKET)
_VALID_STATUSES = {
    "계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당", "현재 자료만으로 판단 불가",
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
    counts = {"high": 0, "medium": 0, "low": 0, "needCheck": 0, "unknown": 0}
    for a in assessments:
        bucket = _LEVEL_BUCKET.get(a["level"], "unknown")
        counts[bucket] += 1
    return counts


def build_data(summary: dict, llm: dict) -> AnalysisData:
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
    return AnalysisData(
        summary=summary,
        riskCounts=RiskCounts(**counts),
        riskAssessments=[RiskAssessment(**m) for m in merged],
        publicDocumentChecks=PUBLIC_DOCUMENT_CHECKS,
        stageChecklists=STAGE_CHECKLISTS,
        questionsByTarget=QUESTIONS_BY_TARGET,
        finalComment=llm.get("finalComment", ""),
        risks=[],
        checklist=CHECKLIST,
        questions_to_ask=QUESTIONS_TO_ASK,
    )
