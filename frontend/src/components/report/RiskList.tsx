import type { Risk, RiskLevel } from '../../types/analysis';
import Card from '../common/Card';
import SectionHeading from '../common/SectionHeading';
import RiskCard from './RiskCard';

const order: Record<RiskLevel, number> = {
  고위험: 0,
  높음: 0,
  주의: 1,
  보통: 1,
  '확인 필요': 2,
  낮음: 3,
};

export default function RiskList({ risks }: { risks: Risk[] }) {
  const sortedRisks = [...risks].sort((a, b) => order[a.level] - order[b.level]);

  return (
    <section id="document-analysis" className="print-section scroll-mt-8">
      <Card className="space-y-5">
        <div className="space-y-2">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <SectionHeading title="문서별 비교 분석" />
            <p className="text-sm font-medium text-brand-muted">현재 자료 기준으로 정렬했어요.</p>
          </div>
          <p className="break-keep text-sm leading-6 text-brand-muted">
            계약서에서 확인 가능한 항목과 공적서류로 추가 확인해야 하는 항목을 나눠 정리했습니다.
          </p>
        </div>
        <div className="space-y-4">
          {sortedRisks.map((risk) => (
            <RiskCard key={risk.id ?? `${risk.level}-${risk.clause}`} risk={risk} />
          ))}
        </div>
      </Card>
    </section>
  );
}
