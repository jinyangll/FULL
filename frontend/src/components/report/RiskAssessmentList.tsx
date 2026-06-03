import type { RiskAssessment, RiskLevel } from '../../types/analysis';
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

export default function RiskAssessmentList({ risks }: { risks: RiskAssessment[] }) {
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
            <article key={risk.id} className="print-card risk-card rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
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
