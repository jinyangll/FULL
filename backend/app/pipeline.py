import logging

from app import upstage
from app.prompt import build_messages
from app.mapper import is_contract, parse_llm_json, build_data
from app.schema import AnalysisResponse, ErrorInfo

logger = logging.getLogger(__name__)

_ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}

_MESSAGES = {
    "not_contract": "임대차계약서로 보이지 않습니다.",
    "ocr_failed": "문서에서 텍스트를 추출하지 못했습니다.",
    "unsupported_format": "PDF, JPG, PNG 형식만 지원합니다.",
    "analysis_failed": "분석 중 오류가 발생했습니다.",
}


def _error(code: str) -> AnalysisResponse:
    return AnalysisResponse(status="error", error=ErrorInfo(code=code, message=_MESSAGES[code]))


def analyze(file_bytes: bytes, filename: str, content_type: str) -> AnalysisResponse:
    if content_type not in _ALLOWED_TYPES:
        return _error("unsupported_format")
    try:
        doc_type = upstage.classify(file_bytes, filename)
        if not is_contract(doc_type):
            return _error("not_contract")

        text = upstage.parse(file_bytes, filename)
        if not text or not text.strip():
            return _error("ocr_failed")

        summary = upstage.extract(text)
        messages = build_messages(text, summary)
        raw = upstage.chat(messages)
        llm = parse_llm_json(raw)
        data = build_data(summary, llm)
        return AnalysisResponse(status="success", data=data)
    except Exception as exc:
        logger.exception("analyze() 실패: %s", exc)
        return _error("analysis_failed")
