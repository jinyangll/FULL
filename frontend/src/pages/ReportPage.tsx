import { ArrowLeft, Printer } from 'lucide-react';
import { Navigate } from 'react-router-dom';
import { Button, ButtonLink } from '../components/common/Button';
import AnalysisScopeCard from '../components/report/AnalysisScopeCard';
import DisclaimerBox from '../components/report/DisclaimerBox';
import Checklist from '../components/report/Checklist';
import FinalCommentBox from '../components/report/FinalCommentBox';
import PublicDocumentCheckSection from '../components/report/PublicDocumentCheckSection';
import QuestionsByTargetSection from '../components/report/QuestionsByTargetSection';
import ReportLayout from '../components/report/ReportLayout';
import RiskOverview from '../components/report/RiskOverview';
import RiskAssessmentList from '../components/report/RiskAssessmentList';
import SummaryCard from '../components/report/SummaryCard';
import StageChecklistTimeline from '../components/report/StageChecklistTimeline';
import { getAnalysis } from '../lib/storage';

export default function ReportPage() {
  const analysis = getAnalysis();

  if (!analysis) {
    return <Navigate to="/" replace />;
  }

  const analyzedAt = new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date());

  const handlePrint = () => {
    document.body.classList.add('is-printing');

    const cleanup = () => {
      document.body.classList.remove('is-printing');
      window.removeEventListener('afterprint', cleanup);
    };

    window.addEventListener('afterprint', cleanup);
    window.print();
    window.setTimeout(cleanup, 1000);
  };

  return (
    <main className="report-page print-report mx-auto max-w-7xl px-5 py-8 sm:px-6 sm:py-10">
      <div className="print-hidden mb-8 flex flex-wrap items-center justify-between gap-3">
        <ButtonLink to="/" variant="link" className="px-0">
          <ArrowLeft size={18} aria-hidden="true" />
          다른 계약서 분석
        </ButtonLink>
        <Button type="button" variant="ghost" onClick={handlePrint}>
          <Printer size={18} aria-hidden="true" />
          PDF로 저장
        </Button>
      </div>

      <div id="summary" className="report-title-card print-section print-card mb-8 scroll-mt-8 rounded-3xl border border-slate-200/80 bg-white/85 p-6 shadow-card backdrop-blur sm:p-8">
        <h1 className="text-3xl font-bold tracking-normal text-brand sm:text-4xl">전월세 계약 사전 점검 리포트</h1>
        <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">분석 일시 {analyzedAt}</p>
        <p className="mt-1 text-sm font-bold text-brand-accent">AI 계약 검토 어시스턴트</p>
        <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">
          계약서와 추가 확인 자료를 구분해 위험 요소를 정리했어요.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {['계약서 기반 분석', '공적서류 추가 확인 필요', '참고용 리포트'].map((badge) => (
            <span key={badge} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold text-brand-muted">
              {badge}
            </span>
          ))}
        </div>
      </div>

      <ReportLayout>
        <AnalysisScopeCard providedDocuments={analysis.providedDocuments} />
        <div id="risk-summary" className="print-section scroll-mt-8">
          <RiskOverview analysis={analysis} />
        </div>
        <SummaryCard summary={analysis.summary} />
        {analysis.riskAssessments ? <RiskAssessmentList risks={analysis.riskAssessments} /> : null}
        {analysis.publicDocumentChecks ? <PublicDocumentCheckSection documents={analysis.publicDocumentChecks} /> : null}
        {analysis.stageChecklists ? <StageChecklistTimeline stages={analysis.stageChecklists} /> : null}
        <Checklist items={analysis.checklist} />
        {analysis.questionsByTarget ? <QuestionsByTargetSection questions={analysis.questionsByTarget} /> : null}
        {analysis.finalComment ? <FinalCommentBox comment={analysis.finalComment} /> : null}
        <DisclaimerBox />
        <div className="print-hidden flex justify-center pt-2">
          <ButtonLink to="/" variant="primary">
            다른 계약서 분석하기
          </ButtonLink>
        </div>
      </ReportLayout>
    </main>
  );
}
