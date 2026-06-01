import { FileText, FileSearch, ListChecks } from 'lucide-react';
import Card from '../common/Card';
import SectionHeading from '../common/SectionHeading';

const scopes = [
  {
    title: '확인한 문서',
    icon: FileText,
    items: ['업로드된 전월세 계약서', '계약서 본문 및 특약', '보증금·월세·계약기간·관리비 등'],
  },
  {
    title: '추가로 필요한 자료',
    icon: FileSearch,
    items: ['등기부등본', '건축물대장', '전입세대확인서', '미납 국세·지방세 열람', '실거래가·안심전세 App', '신탁원부, 필요한 경우'],
  },
  {
    title: '판단 방식',
    icon: ListChecks,
    items: ['계약서에서 확인 가능한 내용은 요약', '외부 자료가 필요한 항목은 추가 확인으로 분류', '계약 전·잔금 전·입주 직후 해야 할 일을 구분'],
  },
];

interface AnalysisScopeCardProps {
  providedDocuments?: string[];
}

export default function AnalysisScopeCard({ providedDocuments }: AnalysisScopeCardProps) {
  return (
    <section id="scope" className="print-section scroll-mt-8">
      <Card className="space-y-5">
        <div>
          <SectionHeading title="현재 리포트가 확인한 범위" />
          <p className="mt-3 break-keep rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm leading-6 text-brand">
            이 리포트는 업로드된 계약서 내용을 기준으로 작성된 사전 점검 결과입니다. 등기부등본,
            건축물대장, 전입세대확인서, 세금 열람 자료 등 외부 공적서류가 필요한 항목은 ‘추가 확인
            필요’로 표시됩니다.
          </p>
          {providedDocuments && providedDocuments.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-sm font-semibold text-brand">검증에 사용된 서류:</span>
              {providedDocuments.map((doc) => (
                <span
                  key={doc}
                  className="rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-semibold text-brand"
                >
                  {doc}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {scopes.map((scope) => {
            const Icon = scope.icon;
            return (
              <article key={scope.title} className="print-card rounded-2xl border border-slate-200 bg-white p-5">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-brand">
                    <Icon size={19} aria-hidden="true" />
                  </span>
                  <h3 className="font-bold text-brand">{scope.title}</h3>
                </div>
                <ul className="mt-4 space-y-2">
                  {scope.items.map((item) => (
                    <li key={item} className="break-keep text-sm leading-6 text-brand-muted">
                      {item}
                    </li>
                  ))}
                </ul>
              </article>
            );
          })}
        </div>
      </Card>
    </section>
  );
}
