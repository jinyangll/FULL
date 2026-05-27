import json
from app.scaffold import RISK_SCAFFOLD, RISK_IDS

_ALLOWED_LEVELS = ["높음", "주의", "낮음", "확인 필요", "판단 불가"]
_ALLOWED_STATUS = ["계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당", "현재 자료만으로 판단 불가"]

_SYSTEM = (
    "당신은 한국 전월세 임대차계약서의 위험 요소를 분석하는 보조 도구입니다. "
    "법률 자문이 아니라 참고용 점검 의견을 제공합니다. "
    "'사기' 같은 단정적 표현 대신 '전세가율 과다', '신탁등기 권리관계' 같은 서술적 표현을 쓰세요. "
    "반드시 지정된 JSON 형식만 출력하고, 그 외 설명 문장은 출력하지 마세요."
)


def _category_guide() -> str:
    lines = []
    for item in RISK_SCAFFOLD:
        lines.append(f'- {item["id"]} ({item["title"]}): {item["whyImportant"]}')
    return "\n".join(lines)


def build_messages(contract_text: str, summary: dict) -> list[dict]:
    user = f"""다음은 분석할 전월세 계약서입니다.

[계약서에서 추출된 요약 정보]
{json.dumps(summary, ensure_ascii=False, indent=2)}

[계약서 본문]
{contract_text}

[분석할 9개 위험 카테고리]
{_category_guide()}

위 9개 카테고리 각각에 대해 이 계약서 기준의 판단을 내려 주세요.
- level 은 다음 중 하나: {_ALLOWED_LEVELS}
- status 는 다음 중 하나: {_ALLOWED_STATUS}
- currentFinding: 이 계약서에서 확인된 사실에 근거한 현재 소견 (2~3문장)
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
