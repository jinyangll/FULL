import json
from app.scaffold import RISK_SCAFFOLD, RISK_IDS, DETECTION_RULES

_ALLOWED_LEVELS = ["높음", "주의", "낮음", "확인 필요", "판단 불가"]
_ALLOWED_STATUS = ["계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당", "현재 자료만으로 판단 불가"]

_SYSTEM = (
    "당신은 한국 전월세 임대차계약서의 위험 요소를 분석하는 보조 도구입니다. "
    "법률 자문이 아니라 참고용 점검 의견을 제공합니다. "
    "'사기' 같은 단정적 표현 대신 '전세가율 과다', '신탁등기 권리관계' 같은 서술적 표현을 쓰세요. "
    "제공된 서류에서 실제로 확인되는 사실만 근거로 삼고, 제출되지 않은 서류의 내용을 추측하지 마세요. "
    "반드시 지정된 JSON 형식만 출력하고, 그 외 설명 문장은 출력하지 마세요."
)


def _category_guide() -> str:
    lines = []
    for item in RISK_SCAFFOLD:
        rule = DETECTION_RULES[item["id"]]
        lines.append(f'- {item["id"]} ({item["title"]}): {item["whyImportant"]}\n  판별 규칙: {rule}')
    return "\n".join(lines)


def _supporting_block(supporting: list[tuple[str, str]]) -> str:
    if not supporting:
        return "(계약서 외 공적서류는 제출되지 않았습니다.)"
    return "\n\n".join(f"[{doc_type}]\n{text}" for doc_type, text in supporting)


def _jeonse_block(jeonse: dict | None) -> str:
    if not jeonse:
        return ""
    return (
        "\n\n[실거래가 자동조회 결과 — 공공데이터로 확인된 확정 사실]\n"
        f"{jeonse['currentFinding']} (출처: {jeonse['dataSource']})\n"
        "이는 국토교통부 실거래가로 확인된 사실입니다. jeonse-price-ratio 항목과 finalComment(총평)에서 "
        "이 전세가율을 확정 사실로 다루고, '시세 확인이 필요하다'거나 '~일 가능성'처럼 추측하는 표현은 쓰지 마세요."
    )


def _blacklist_block(landlord: dict | None) -> str:
    if not landlord:
        return ""
    return (
        "\n\n[악성임대인 명단 대조 결과 — 공개 명단과 인적사항 일치]\n"
        f"{landlord['currentFinding']} (출처: {landlord['dataSource']})\n"
        "multi-home-landlord 항목과 finalComment(총평)에서 이 사실을 반영하되, "
        "'사기범'처럼 단정하지 말고 '공개 명단과 인적사항이 일치하므로 직접 확인이 필요하다'는 톤으로 서술하세요."
    )


def build_messages(contract_text: str, summary: dict, supporting: list[tuple[str, str]],
                   jeonse: dict | None = None, landlord: dict | None = None) -> list[dict]:
    provided = ["임대차계약서"] + [doc_type for doc_type, _ in supporting]
    user = f"""다음은 분석할 전월세 계약 건의 서류 묶음입니다.

[제출된 서류 목록]
{", ".join(provided)}

[계약서에서 추출된 요약 정보]
{json.dumps(summary, ensure_ascii=False, indent=2)}

[계약서 본문]
{contract_text}

[함께 제출된 공적서류]
{_supporting_block(supporting)}{_jeonse_block(jeonse)}{_blacklist_block(landlord)}

[분석할 9개 위험 카테고리와 판별 규칙]
{_category_guide()}

위 9개 카테고리 각각에 대해, 제출된 서류에서 확인되는 사실만 근거로 판단하세요.
- 판별에 필요한 서류가 제출되지 않았으면 추측하지 말고 status="외부 서류 확인 필요", level="확인 필요"(또는 판단 불가)로 두세요.
- 여러 서류를 대조해야 하는 항목(예: 임대인 신원=계약서 임대인↔등기부 갑구 소유자)은 실제 대조 결과를 currentFinding에 적으세요.
- level 은 다음 중 하나: {_ALLOWED_LEVELS}
- status 는 다음 중 하나: {_ALLOWED_STATUS}
- currentFinding: 제출된 서류에서 확인된 사실에 근거한 현재 소견 (2~3문장)
- action: 사용자가 취할 구체적 행동
- questions: 임대인/중개사에게 물어볼 질문 1~3개

아래 JSON 형식으로만 출력하세요. assessments 의 키는 반드시 다음 9개여야 합니다:
{RISK_IDS}

{{
  "assessments": {{
    "<category_id>": {{ "level": "...", "status": "...", "currentFinding": "...", "action": "...", "questions": ["..."] }}
  }},
  "finalComment": "전체 계약에 대한 2~4문장 총평"
}}"""
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user},
    ]
