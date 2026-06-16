import { ArrowLeft } from 'lucide-react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { ButtonLink } from '../components/common/Button';
import ContractViewer from '../components/report/ContractViewer';
import { getAnalysis } from '../lib/storage';

export default function ContractPage() {
  const analysis = getAnalysis();
  const [searchParams] = useSearchParams();

  if (!analysis || !analysis.contractText || !analysis.riskAssessments) {
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
      <h1 className="text-2xl font-bold text-brand sm:text-3xl">계약서 원문</h1>
      <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
        분석에서 위험 근거로 인용된 부분을 등급별 색으로 강조했습니다.
        보고서의 위험 항목에서 “원문에서 보기”를 누르면 해당 위치로 이동합니다.
      </p>
      <div className="mt-6">
        <ContractViewer text={analysis.contractText} risks={analysis.riskAssessments} activeRiskId={focus} />
      </div>
    </main>
  );
}
