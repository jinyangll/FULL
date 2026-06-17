"""리포트 챗봇: 분석 결과(AnalysisData dict)를 근거로만 답한다."""
from app import upstage

_SYSTEM = (
    "당신은 전월세 임대차계약서 분석 리포트에 대해 사용자의 질문에 답하는 보조 도구입니다. "
    "아래 [분석 리포트] 내용만 근거로 답하세요. "
    "리포트에 없는 일반 법률 질문이나 이 계약 건과 무관한 질문은 정중히 거절하고, "
    "이 리포트로 답할 수 있는 범위를 안내하세요. "
    "사람 이름·금액·날짜처럼 특정 사실을 물으면 리포트에 적힌 값만 그대로 답하고, "
    "리포트에 그 값이 없으면 추측하지 말고 '리포트에 해당 정보가 없습니다'라고 답하세요. "
    "특히 임대인/임차인 등 계약 당사자를 물으면 [계약 요약]의 임대인/임차인 항목만 보고 답하고, "
    "위험 항목 분석에 등장하는 다른 이름(예: 과거 소유자)과 혼동하지 마세요. "
    "보증금 대비 시세·실거래가·전세가율 관련 질문을 받으면, '전세가율' 위험 항목의 분석 내용에 "
    "실거래가 중앙값과 표본 수가 들어 있으니 그 값을 근거로 답하세요. "
    "법률 자문이 아니라 참고용 설명이며, '사기다' 같은 단정 표현은 쓰지 마세요. "
    "한국어로 쉽고 간결하게 답하세요."
)


def _format_context(ctx: dict) -> str:
    lines: list[str] = []

    summary = ctx.get("summary") or {}
    if summary:
        lines.append("[계약 요약]")
        for key, label in (
            ("type", "계약 종류"),
            ("parties", "임대인/임차인"),
            ("deposit", "보증금"),
            ("monthlyRent", "월세"),
            ("duration", "기간"),
            ("moveInDate", "입주일"),
            ("balanceDate", "잔금일"),
            ("maintenanceFee", "관리비"),
            ("realtor", "중개사"),
            ("address", "주소"),
        ):
            value = summary.get(key)
            if value:
                lines.append(f"- {label}: {value}")

    assessments = ctx.get("riskAssessments") or []
    if assessments:
        lines.append("\n[위험 항목별 분석]")
        for a in assessments:
            lines.append(
                f"- {a.get('title', '')} "
                f"[위험도 {a.get('level', '')} / {a.get('status', '')}]: "
                f"{a.get('currentFinding', '')} → {a.get('action', '')}"
            )

    final = ctx.get("finalComment")
    if final:
        lines.append(f"\n[최종 코멘트]\n{final}")

    checklist = ctx.get("checklist") or []
    if checklist:
        lines.append("\n[체크리스트]")
        lines.extend(f"- {item}" for item in checklist)

    return "\n".join(lines)


def build_chat_messages(messages: list[dict], context: dict) -> list[dict]:
    system = _SYSTEM + "\n\n[분석 리포트]\n" + _format_context(context)
    return [{"role": "system", "content": system}, *messages]


def answer(messages: list[dict], context: dict) -> str:
    return upstage.converse(build_chat_messages(messages, context))
