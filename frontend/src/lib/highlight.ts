import type { RiskLevel, SourceDocument } from '../types/analysis';

export interface HighlightInput {
  quote: string;
  level: RiskLevel;
  riskId: string;
}

export interface Segment {
  text: string;
  level?: RiskLevel;
  riskId?: string;
  anchor?: boolean; // 해당 위험 항목의 첫 등장 — 스크롤 타깃
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 토큰(글자·숫자) 사이는 공백·구두점·기호를 0개 이상 허용해 유연하게 매칭한다.
// PDF 파싱은 공백을 붙이거나, evidence(LLM 정규화)는 콜론·중간점·괄호를 더하거나 빼는
// 경우가 많아 원문과 자주 어긋나기 때문이다. (예: "주택 유형: 아파트" ↔ 원문 "주택 유형 아파트")
const TOKEN_SEP = '[\\s\\p{P}\\p{S}]*';

function buildPattern(quote: string): string | null {
  const tokens = quote.trim().split(/[\s\p{P}\p{S}]+/u).filter(Boolean);
  if (tokens.length === 0) return null;
  return tokens.map(escapeRegExp).join(TOKEN_SEP);
}

/** 위험 등급별 하이라이트 배경색(원문 발췌·뷰어 공용). */
export const LEVEL_MARK_CLASS: Record<RiskLevel, string> = {
  고위험: 'bg-red-100 text-red-900',
  높음: 'bg-red-100 text-red-900',
  주의: 'bg-amber-100 text-amber-900',
  보통: 'bg-amber-100 text-amber-900',
  '확인 필요': 'bg-blue-100 text-blue-900',
  낮음: 'bg-emerald-100 text-emerald-900',
};

interface Interval {
  start: number;
  end: number;
  level: RiskLevel;
  riskId: string;
}

export interface Snippet {
  before: string; // 위험 부분 앞 문맥(잘린 경우 앞에 … 포함)
  match: string; // 위험 부분(강조 대상) — 원문 표기 그대로
  after: string; // 위험 부분 뒤 문맥(잘린 경우 뒤에 … 포함)
}

/**
 * 계약서 원문에서 인용구 위치를 찾아 앞뒤 pad 글자만큼의 문맥과 함께 발췌한다.
 * 위험 부분(match)은 원문 표기 그대로 돌려줘 카드 안에서 바로 강조해 보여줄 수 있다.
 * 못 찾으면 null(이 경우 호출부가 인용구 원문을 그대로 표시).
 */
export function extractSnippet(text: string, quote: string, pad = 40): Snippet | null {
  if (!text) return null;
  const pattern = buildPattern(quote);
  if (pattern === null) return null;
  let re: RegExp;
  try {
    re = new RegExp(pattern, 'u');
  } catch {
    return null;
  }
  const m = re.exec(text);
  if (!m) return null;
  const start = m.index;
  const end = start + m[0].length;
  const beforeStart = Math.max(0, start - pad);
  const afterEnd = Math.min(text.length, end + pad);
  return {
    before: (beforeStart > 0 ? '…' : '') + text.slice(beforeStart, start),
    match: m[0],
    after: text.slice(end, afterEnd) + (afterEnd < text.length ? '…' : ''),
  };
}

/**
 * 여러 원본 문서(계약서·등기부등본 등)에서 인용구를 차례로 찾아 첫 발췌를 돌려준다.
 * 근거가 어느 문서에서 나왔든 그 문서에서 강조해 보여주기 위함이다. 못 찾으면 null.
 */
export function extractSnippetFromDocs(
  docs: SourceDocument[] | undefined,
  quote: string,
  pad = 40,
): Snippet | null {
  for (const doc of docs ?? []) {
    const snippet = extractSnippet(doc.text, quote, pad);
    if (snippet) return snippet;
  }
  return null;
}

/**
 * 문서 원문에서 evidence 인용구 위치를 찾아 하이라이트 구간으로 쪼갠다.
 * 인용구는 원문 그대로지만 PDF 파싱/줄바꿈 차이가 있을 수 있어 공백·구두점은 유연하게 매칭한다.
 * 겹치는 구간은 먼저 시작한 것을 우선한다. 못 찾은 인용구는 조용히 건너뛴다.
 */
export function buildHighlightSegments(text: string, highlights: HighlightInput[]): Segment[] {
  if (!text) return [];

  const intervals: Interval[] = [];
  const seen = new Set<string>();
  for (const { quote, level, riskId } of highlights) {
    const key = `${riskId}::${quote}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const pattern = buildPattern(quote);
    if (pattern === null) continue;
    let re: RegExp;
    try {
      re = new RegExp(pattern, 'gu');
    } catch {
      continue;
    }
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      if (m[0].length === 0) {
        re.lastIndex += 1;
        continue;
      }
      intervals.push({ start: m.index, end: m.index + m[0].length, level, riskId });
    }
  }

  // 시작 위치 오름차순, 동일 시작이면 긴 구간 우선. 겹치면 뒤엣것 버림.
  intervals.sort((a, b) => a.start - b.start || b.end - a.end);
  const chosen: Interval[] = [];
  let lastEnd = -1;
  for (const iv of intervals) {
    if (iv.start >= lastEnd) {
      chosen.push(iv);
      lastEnd = iv.end;
    }
  }

  const segments: Segment[] = [];
  const anchored = new Set<string>();
  let cursor = 0;
  for (const iv of chosen) {
    if (iv.start > cursor) {
      segments.push({ text: text.slice(cursor, iv.start) });
    }
    const isAnchor = !anchored.has(iv.riskId);
    anchored.add(iv.riskId);
    segments.push({
      text: text.slice(iv.start, iv.end),
      level: iv.level,
      riskId: iv.riskId,
      anchor: isAnchor,
    });
    cursor = iv.end;
  }
  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor) });
  }
  return segments;
}
