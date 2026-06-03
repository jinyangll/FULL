import { AlertTriangle, CircleAlert, FileSearch, ShieldCheck } from 'lucide-react';
import type { AnalysisData } from '../../types/analysis';

const overview: Array<{
  countKey: 'high' | 'medium' | 'low' | 'needCheck';
  label: string;
  description: string;
  className: string;
  iconBoxClassName: string;
  icon: typeof AlertTriangle;
}> = [
  {
    countKey: 'high',
    label: '고위험',
    description: '계약 전 우선 확인',
    className: 'risk-summary-high border-risk-high-border bg-risk-high-bg text-risk-high-text',
    iconBoxClassName: 'bg-white/75 text-risk-high-text',
    icon: AlertTriangle,
  },
  {
    countKey: 'medium',
    label: '주의',
    description: '조건을 더 명확히 확인',
    className: 'risk-summary-medium border-risk-medium-border bg-risk-medium-bg text-risk-medium-text',
    iconBoxClassName: 'bg-white/75 text-risk-medium-text',
    icon: CircleAlert,
  },
  {
    countKey: 'needCheck',
    label: '확인 필요',
    description: '외부 자료 필요',
    className: 'risk-summary-low border-risk-low-border bg-risk-low-bg text-risk-low-text',
    iconBoxClassName: 'bg-white/75 text-risk-low-text',
    icon: FileSearch,
  },
  {
    countKey: 'low',
    label: '낮음',
    description: '기본 확인 후 유지',
    className: 'risk-summary-low border-risk-low-border bg-risk-low-bg text-risk-low-text',
    iconBoxClassName: 'bg-white/75 text-risk-low-text',
    icon: ShieldCheck,
  },
];

export default function RiskOverview({ analysis }: { analysis: AnalysisData }) {
  const fallbackCounts = {
    high: analysis.risks.filter((risk) => risk.level === '높음' || risk.level === '고위험').length,
    medium: analysis.risks.filter((risk) => risk.level === '보통' || risk.level === '주의').length,
    low: analysis.risks.filter((risk) => risk.level === '낮음').length,
    needCheck: analysis.risks.filter((risk) => risk.level === '확인 필요').length,
  };
  const counts = analysis.riskCounts ?? fallbackCounts;

  return (
    <section className="risk-overview grid gap-4">
      {overview.map((item) => {
        const Icon = item.icon;
        return (
          <article
            key={item.countKey}
            className={`risk-summary-card print-card rounded-2xl border p-5 shadow-sm ${item.className}`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`risk-summary-icon flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${item.iconBoxClassName}`}
              >
                <Icon size={21} strokeWidth={2.2} aria-hidden="true" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <h2 className="risk-summary-title text-base font-bold">{item.label}</h2>
                  <p className="risk-summary-count whitespace-nowrap text-2xl font-bold tracking-normal">
                    {counts[item.countKey]}건
                  </p>
                </div>
                <p className="mt-1 break-keep text-sm opacity-80">{item.description}</p>
              </div>
            </div>
          </article>
        );
      })}
    </section>
  );
}
