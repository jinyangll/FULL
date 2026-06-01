import type { AnalysisSummary } from '../../types/analysis';
import Card from '../common/Card';
import SectionHeading from '../common/SectionHeading';

const labels: Array<{ key: keyof AnalysisSummary; label: string }> = [
  { key: 'type', label: '계약 유형' },
  { key: 'parties', label: '임대인 / 임차인' },
  { key: 'deposit', label: '보증금' },
  { key: 'monthlyRent', label: '월세' },
  { key: 'duration', label: '계약 기간' },
  { key: 'moveInDate', label: '입주일' },
  { key: 'balanceDate', label: '잔금일' },
  { key: 'maintenanceFee', label: '관리비' },
  { key: 'realtor', label: '중개사 정보' },
];

export default function SummaryCard({ summary }: { summary: AnalysisSummary }) {
  return (
    <section id="contract-info" className="print-section scroll-mt-8">
      <Card className="space-y-5">
        <div>
          <SectionHeading title="계약 기본정보" />
          <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
            계약서에서 추출한 핵심 정보를 먼저 확인합니다. 비어 있는 항목은 추가 확인이 필요합니다.
          </p>
        </div>
        <dl className="summary-grid grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {labels.map((item) => (
            <div key={item.key} className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
              <dt className="text-xs font-bold text-brand-muted">{item.label}</dt>
              <dd className="mt-2 break-keep text-sm font-bold text-brand">{summary[item.key] ?? '추가 확인 필요'}</dd>
            </div>
          ))}
        </dl>
      </Card>
    </section>
  );
}
