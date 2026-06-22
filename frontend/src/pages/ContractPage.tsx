import { ArrowLeft } from 'lucide-react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { ButtonLink } from '../components/common/Button';
import ContractViewer from '../components/report/ContractViewer';
import { getAnalysis, resolveSourceDocuments } from '../lib/storage';

export default function ContractPage() {
  const analysis = getAnalysis();
  const [searchParams] = useSearchParams();
  const sourceDocs = analysis ? resolveSourceDocuments(analysis) : undefined;

  if (!analysis || !sourceDocs || !analysis.riskAssessments) {
    return <Navigate to="/report" replace />;
  }

  const focus = searchParams.get('focus');
  const backTo = focus ? `/report?tab=detail#risk-${focus}` : '/report?tab=detail';

  return (
    <main className="mx-auto max-w-4xl px-5 py-8 sm:px-6 sm:py-10">
      <div className="mb-6">
        <ButtonLink to={backTo} variant="link" className="px-0">
          <ArrowLeft size={18} aria-hidden="true" />
          보고서로 돌아가기
        </ButtonLink>
      </div>
      <h1 className="text-2xl font-bold text-brand sm:text-3xl">문서 원문</h1>
      <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
        분석에서 위험 근거로 인용된 부분을 등급별 색으로 강조했습니다. 근거가 나온 문서(계약서·등기부등본 등)에서
        해당 위치를 확인할 수 있고, 보고서의 위험 항목에서 “원문에서 보기”를 누르면 해당 위치로 이동합니다.
      </p>
      <div className="mt-6 space-y-8">
        {sourceDocs.map((doc) => (
          <section key={doc.docType}>
            <h2 className="mb-2 text-sm font-bold text-brand-accent">{doc.docType}</h2>
            <ContractViewer text={doc.text} risks={analysis.riskAssessments!} activeRiskId={focus} />
          </section>
        ))}
      </div>
    </main>
  );
}
