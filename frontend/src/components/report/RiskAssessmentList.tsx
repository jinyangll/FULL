import type { RiskAssessment, RiskLevel, SourceDocument } from '../../types/analysis';
import { extractSnippetFromDocs, LEVEL_MARK_CLASS, type Snippet } from '../../lib/highlight';
import Badge from '../common/Badge';
import Card from '../common/Card';
import SectionHeading from '../common/SectionHeading';

const order: Record<RiskLevel, number> = {
  고위험: 0,
  높음: 0,
  주의: 1,
  보통: 1,
  '확인 필요': 2,
  낮음: 3,
};

const statusClasses: Record<RiskAssessment['status'], string> = {
  '계약서에서 확인됨': 'border-emerald-200 bg-emerald-50 text-emerald-800',
  '외부 서류 확인 필요': 'border-blue-200 bg-blue-50 text-blue-800',
  '조건부 해당': 'border-amber-200 bg-amber-50 text-amber-800',
};

export default function RiskAssessmentList({
  risks,
  onSelectRisk,
  activeRiskId,
  sourceDocuments,
}: {
  risks: RiskAssessment[];
  onSelectRisk?: (id: string) => void;
  activeRiskId?: string | null;
  sourceDocuments?: SourceDocument[];
}) {
  const sorted = [...risks].sort((a, b) => order[a.level] - order[b.level]);

  return (
    <section id="document-analysis" className="print-section scroll-mt-8">
      <Card className="space-y-5">
        <div>
          <SectionHeading title="문서별 비교 분석" />
          <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
            계약서에서 확인 가능한 항목과 공적서류로 추가 확인해야 하는 항목을 나눠 정리했습니다.
          </p>
        </div>
        <div className="space-y-4">
          {sorted.map((risk) => (
            <article key={risk.id} id={`risk-${risk.id}`} className="print-card risk-card scroll-mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
              <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 pb-4">
                <div>
                  <p className="text-xs font-bold text-brand-accent">{risk.category}</p>
                  <h3 className="mt-1 text-lg font-bold text-brand">{risk.title}</h3>
                </div>
                <div className="flex flex-wrap justify-end gap-2">
                  <span className={`rounded-full border px-3 py-1 text-xs font-bold ${statusClasses[risk.status]}`}>
                    {risk.status}
                  </span>
                  <Badge level={risk.level} />
                </div>
              </div>
              <div className="mt-4 grid gap-3 lg:grid-cols-2">
                <InfoBlock title="확인해야 할 자료" value={risk.requiredDocuments.join(', ')} />
                <InfoBlock title="계약서에서 찾은 단서" value={risk.contractClues.join(', ')} />
                <InfoBlock title="확인 시점" value={risk.stages.join(' / ')} />
                <InfoBlock title="분류 기준" value={risk.status} />
              </div>
              <div className="mt-4 space-y-3">
                <InfoBlock title="왜 중요한가" value={risk.whyImportant} />
                <InfoBlock title="현재 자료 기준 판단" value={risk.currentFinding} source={risk.dataSource} />
                {(() => {
                  if (!risk.evidence || risk.evidence.length === 0) return null;
                  // 근거 인용구를 원본 문서들(계약서·등기부등본 등)에서 찾아본다. 어느 문서에서든
                  // 찾아진 것만 원문 페이지로 이동하는 링크로 만들고, 못 찾으면 일반 텍스트로 둔다.
                  const items = risk.evidence.map((quote) => ({
                    quote,
                    snippet: extractSnippetFromDocs(sourceDocuments, quote),
                  }));
                  const hasSourceEvidence = items.some((it) => it.snippet !== null);
                  return (
                    <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                      <p className="text-xs font-bold text-brand-muted">
                        근거
                        {onSelectRisk && hasSourceEvidence ? (
                          <span className="ml-1 font-medium text-brand-accent">· 클릭하면 원문에서 위치 보기 →</span>
                        ) : null}
                      </p>
                      <ul className="mt-2 space-y-2">
                        {items.map(({ quote, snippet }) =>
                          onSelectRisk && snippet ? (
                            <li key={quote}>
                              <button
                                type="button"
                                onClick={() => onSelectRisk(risk.id)}
                                className={`block w-full break-keep border-l-4 px-3 py-2 text-left text-sm leading-6 text-brand transition hover:bg-slate-100 ${
                                  activeRiskId === risk.id ? 'border-brand-accent bg-slate-100' : 'border-slate-300 bg-slate-50'
                                }`}
                              >
                                <EvidenceContent snippet={snippet} quote={quote} level={risk.level} />
                              </button>
                            </li>
                          ) : (
                            <li
                              key={quote}
                              className="break-keep border-l-4 border-slate-300 bg-slate-50 px-3 py-2 text-sm leading-6 text-brand"
                            >
                              <EvidenceContent snippet={snippet} quote={quote} level={risk.level} />
                            </li>
                          ),
                        )}
                      </ul>
                    </div>
                  );
                })()}
                <InfoBlock title="지금 해야 할 확인 행동" value={risk.action} emphasis />
              </div>
              <div className="mt-4">
                <p className="text-xs font-bold text-brand-muted">질문 예시</p>
                <ul className="mt-2 grid gap-2 md:grid-cols-2">
                  {risk.questions.slice(0, 2).map((question) => (
                    <li key={question} className="break-keep rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-brand">
                      {question}
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          ))}
        </div>
      </Card>
    </section>
  );
}

function EvidenceContent({
  snippet,
  quote,
  level,
}: {
  snippet: Snippet | null;
  quote: string;
  level: RiskLevel;
}) {
  // 원문에서 못 찾으면(외부 서류 근거·파싱 차이 등) 인용구 자체를 그대로 보여준다.
  if (!snippet) {
    return <span className="italic">“{quote}”</span>;
  }
  return (
    <span className="break-keep">
      <span className="text-brand-muted">{snippet.before}</span>
      <mark className={`rounded px-1 font-semibold ${LEVEL_MARK_CLASS[level]}`}>{snippet.match}</mark>
      <span className="text-brand-muted">{snippet.after}</span>
    </span>
  );
}

function InfoBlock({ title, value, emphasis = false, source }: { title: string; value: string; emphasis?: boolean; source?: string }) {
  return (
    <div className={`rounded-2xl border px-4 py-3 ${emphasis ? 'border-blue-100 bg-blue-50' : 'border-slate-200 bg-slate-50'}`}>
      <div className="flex flex-wrap items-center gap-2">
        <p className={`text-xs font-bold ${emphasis ? 'text-brand-accent' : 'text-brand-muted'}`}>{title}</p>
        {source && (
          <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 ring-1 ring-emerald-200">
            ✓ {source}
          </span>
        )}
      </div>
      <p className="mt-2 break-keep text-sm leading-6 text-brand">{value}</p>
    </div>
  );
}
