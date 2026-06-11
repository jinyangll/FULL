"""Upstage API 래퍼.

★ 사용자 작업 영역 ★
아래 4개 함수의 본문(_real_*)을 Upstage 실제 호출로 채우세요.
인터페이스(인자/반환 타입)는 바꾸지 마세요. pipeline 이 이 시그니처에 의존합니다.

- classify(file_bytes, filename) -> str        : 문서 종류 라벨 (예: "임대차계약서")
- parse(file_bytes, filename)    -> str         : 문서 전체 텍스트 (Document Parse)
- extract(text)                  -> dict        : summary 사실 필드 (Universal Extraction)
- chat(messages)                 -> str         : LLM 응답 원문 (JSON 문자열 기대)

USE_FAKE_UPSTAGE=true 면 캔드 데이터를 반환합니다 (키 없이 데모/테스트용).
"""
import base64
import json
import os
import time


def _fake() -> bool:
    return os.getenv("USE_FAKE_UPSTAGE", "false").lower() == "true"


class RateLimitExceeded(Exception):
    """Upstage API rate limit(429)이 재시도 후에도 해소되지 않음."""


_RETRY_WAITS = [2, 5]  # 429 발생 시 재시도 간 대기(초)


def _is_rate_limit(exc: Exception) -> bool:
    resp = getattr(exc, "response", None)
    if resp is not None and getattr(resp, "status_code", None) == 429:
        return True
    return getattr(exc, "status_code", None) == 429


def _with_retry(fn):
    """429면 짧게 대기 후 재시도하고, 끝내 실패하면 RateLimitExceeded 로 변환한다."""
    last = None
    for wait in [0, *_RETRY_WAITS]:
        if wait:
            time.sleep(wait)
        try:
            return fn()
        except Exception as exc:
            if _is_rate_limit(exc):
                last = exc
                continue
            raise
    raise RateLimitExceeded() from last


# ---------- Fake (데모/테스트용) ----------

def _fake_summary() -> dict:
    return {
        "type": "전세 임대차 계약",
        "parties": "임대인 OOO, 임차인 OOO",
        "deposit": "100,000,000원",
        "monthlyRent": "없음",
        "duration": "2024.06.01 ~ 2026.05.31",
        "moveInDate": "2024.06.01",
        "balanceDate": "2024.05.31",
        "maintenanceFee": "월 80,000원, 세부 항목 추가 확인 필요",
        "realtor": "OO공인중개사무소, 중개사 OOO",
        "address": "서울특별시 종로구 청운동 1-1",
        "buildingName": "OO아파트",
        "exclusiveArea": "84.97",
        "propertyType": "아파트",
    }


def _fake_chat_json() -> str:
    from app.scaffold import RISK_IDS
    assessments = {
        rid: {
            "level": "확인 필요",
            "status": "외부 서류 확인 필요",
            "currentFinding": "계약서 기준으로는 확인되나 외부 자료 대조가 필요합니다.",
            "action": "관련 공적 서류를 확인하세요.",
            "questions": ["관련 증빙을 보여줄 수 있나요?"],
        }
        for rid in RISK_IDS
    }
    return json.dumps({
        "assessments": assessments,
        "finalComment": "현재 업로드된 계약서 기준으로는 일부 항목만 확인됩니다. 외부 자료 확인 후 계약을 진행하세요.",
    }, ensure_ascii=False)


def _fake_converse() -> str:
    return "이 리포트를 기준으로 보면, 가장 먼저 확인할 항목은 전세가율입니다. (데모 응답)"


# ---------- 실제 Upstage 호출 (_real_*) ----------

def _api_key() -> str:
    key = os.getenv("UPSTAGE_API_KEY")
    if not key:
        raise RuntimeError("UPSTAGE_API_KEY 가 설정되지 않았습니다 (backend/.env 확인).")
    return key


def _client(path: str = ""):
    from openai import OpenAI
    return OpenAI(api_key=_api_key(), base_url=f"https://api.upstage.ai/v1{path}")


def _real_classify(file_bytes: bytes, filename: str) -> str:
    """document-classify 로 문서 종류를 분류한다. 카테고리는 우리가 정의한다."""
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    resp = _client("/document-classification").chat.completions.create(
        model="document-classify",
        messages=[{
            "role": "user",
            "content": [{
                "type": "image_url",
                "image_url": {"url": f"data:application/octet-stream;base64,{b64}"},
            }],
        }],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document-classify",
                "schema": {
                    "type": "string",
                    "oneOf": [
                        {"const": "임대차계약서", "description": "주택·상가 전세 또는 월세 임대차 계약서"},
                        {"const": "등기부등본", "description": "부동산 등기사항전부증명서"},
                        {"const": "건축물대장", "description": "건축물대장 (일반/집합)"},
                        {"const": "전입세대확인서", "description": "전입세대 열람 내역서"},
                        {"const": "미납국세열람내역", "description": "미납 국세·지방세 열람 내역 또는 납세증명서"},
                        {"const": "신탁원부", "description": "신탁원부"},
                        {"const": "중개대상물확인서", "description": "중개대상물 확인·설명서"},
                        {"const": "기타", "description": "그 외 모든 문서"},
                    ],
                },
            },
        },
    )
    raw = resp.choices[0].message.content
    try:
        label = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        label = raw
    return str(label).strip()


def _real_parse(file_bytes: bytes, filename: str) -> str:
    """document-digitization(Document Parse) 으로 전체 텍스트를 추출한다."""
    import requests
    resp = requests.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {_api_key()}"},
        files={"document": (filename, file_bytes)},
        data={"ocr": "force", "model": "document-parse", "output_formats": '["markdown"]'},
        timeout=120,
    )
    resp.raise_for_status()
    content = resp.json().get("content", {})
    return content.get("markdown") or content.get("text") or content.get("html") or ""


def _real_extract(text: str) -> dict:
    """파싱된 계약서 텍스트에서 summary 사실 필드를 JSON 으로 추출한다."""
    schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "description": "계약 종류 (예: 전세 임대차 계약, 월세 임대차 계약)"},
            "parties": {"type": "string", "description": "임대인/임차인 정보"},
            "deposit": {"type": "string", "description": "보증금 (금액 표기)"},
            "duration": {"type": "string", "description": "임대차 기간 (시작 ~ 종료)"},
            "monthlyRent": {"type": "string", "description": "월세 (없으면 '없음')"},
            "moveInDate": {"type": "string", "description": "입주일"},
            "balanceDate": {"type": "string", "description": "잔금일"},
            "maintenanceFee": {"type": "string", "description": "관리비"},
            "realtor": {"type": "string", "description": "공인중개사 정보"},
            "address": {"type": "string", "description": "임대차 목적물(주택)의 소재지 주소. [부동산의 표시]·[목적물] 항목의 소재지이며, 임대인·임차인 등 계약 당사자의 주소가 아니다. 도로명 또는 지번 전체(건물명·동·호 포함), 없으면 '확인 필요'"},
            "buildingName": {"type": "string", "description": "건물명/아파트명 (없으면 '없음')"},
            "exclusiveArea": {"type": "string", "description": "전용면적 ㎡ 숫자만 (예: 84.97, 없으면 '확인 필요')"},
            "propertyType": {"type": "string", "description": "주택 유형: 아파트/연립다세대/단독다가구/오피스텔 중 하나, 불명확하면 '확인 필요'"},
        },
        "required": ["type", "parties", "deposit", "duration"],
    }
    resp = _client().chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": "임대차계약서 텍스트에서 요약 정보를 추출해 JSON 으로만 답하라. 값을 확인할 수 없으면 '확인 필요' 로 채워라."},
            {"role": "user", "content": text},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "summary", "schema": schema},
        },
    )
    return json.loads(resp.choices[0].message.content)


def _real_chat(messages: list[dict]) -> str:
    """solar-pro3(reasoning) 으로 위험 판단 JSON 을 생성한다."""
    resp = _client().chat.completions.create(
        model="solar-pro3",
        messages=messages,
        reasoning_effort="high",
        stream=False,
    )
    return resp.choices[0].message.content


def _real_converse(messages: list[dict]) -> str:
    """solar-pro3 으로 챗봇 답변을 생성한다. 속도 우선으로 reasoning_effort 를 낮춘다."""
    resp = _client().chat.completions.create(
        model="solar-pro3",
        messages=messages,
        reasoning_effort="low",
        stream=False,
    )
    return resp.choices[0].message.content


# ---------- 공개 인터페이스 (pipeline 이 호출) ----------

_FAKE_CLASSIFY_KEYWORDS = [
    ("등기", "등기부등본"),
    ("건축물", "건축물대장"),
    ("전입", "전입세대확인서"),
    ("국세", "미납국세열람내역"),
    ("신탁", "신탁원부"),
    ("중개", "중개대상물확인서"),
]


def _fake_classify(filename: str) -> str:
    for kw, label in _FAKE_CLASSIFY_KEYWORDS:
        if kw in filename:
            return label
    return "임대차계약서"


def classify(file_bytes: bytes, filename: str) -> str:
    if _fake():
        return _fake_classify(filename)
    return _with_retry(lambda: _real_classify(file_bytes, filename))


def parse(file_bytes: bytes, filename: str) -> str:
    if _fake():
        return "전세 임대차 계약서\n보증금 일억원\n임대인 OOO 임차인 OOO\n특약사항 ..."
    return _with_retry(lambda: _real_parse(file_bytes, filename))


def extract(text: str) -> dict:
    if _fake():
        return _fake_summary()
    return _with_retry(lambda: _real_extract(text))


def chat(messages: list[dict]) -> str:
    if _fake():
        return _fake_chat_json()
    return _with_retry(lambda: _real_chat(messages))


def converse(messages: list[dict]) -> str:
    if _fake():
        return _fake_converse()
    return _with_retry(lambda: _real_converse(messages))
