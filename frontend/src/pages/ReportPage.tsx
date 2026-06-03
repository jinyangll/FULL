import { ArrowLeft, Printer } from 'lucide-react';
import { Navigate, useSearchParams } from 'react-router-dom';
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
import ChatWidget from '../components/report/ChatWidget';
import { getAnalysis } from '../lib/storage';

const TABS = ['summary', 'detail', 'action'] as const;
type ReportTab = (typeof TABS)[number];

export default function ReportPage() {
  const analysis = getAnalysis();
  const [searchParams] = useSearchParams();

  if (!analysis) {
    return <Navigate to="/" replace />;
  }

  const tabParam = searchParams.get('tab');
  const activeTab: ReportTab = TABS.includes(tabParam as ReportTab) ? (tabParam as ReportTab) : 'summary';
  const groupClass = (tab: ReportTab) =>
    `report-group space-y-8${activeTab === tab ? ' active' : ''}`;

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

      <div id="summary" className="report-title-card print-section print-card mb-8 scroll-mt-8 rounded-2xl border border-slate-200/80 bg-white p-6 shadow-card sm:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-bold text-brand-accent">HERO 계약서·공적서류 분리 리포트</p>
            <h1 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              전월세 계약 사전 점검 리포트
            </h1>
            <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">
              계약서에서 확인 가능한 항목과 등기부등본·건축물대장·세금 열람처럼 추가 확인이 필요한 항목을
              구분해 정리했습니다.
            </p>
            <p className="mt-3 text-sm font-semibold text-brand-muted">분석 일시 {analyzedAt}</p>
          </div>
          <div className="grid gap-2 sm:grid-cols-3 lg:w-[360px]">
            {[
              { label: '계약서 기반', value: '확인됨' },
              { label: '공적서류', value: '추가 확인' },
              { label: '리포트 용도', value: '참고용' },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="text-xs font-bold text-brand-muted">{item.label}</p>
                <p className="mt-1 text-sm font-bold text-brand">{item.value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <ReportLayout>
        <div className={groupClass('summary')} data-group="summary">
          {analysis.finalComment ? <FinalCommentBox comment={analysis.finalComment} /> : null}
          <div id="risk-summary" className="print-section scroll-mt-8">
            <RiskOverview analysis={analysis} />
          </div>
          <AnalysisScopeCard providedDocuments={analysis.providedDocuments} />
        </div>

        <div className={groupClass('detail')} data-group="detail">
          <SummaryCard summary={analysis.summary} />
          {analysis.riskAssessments ? <RiskAssessmentList risks={analysis.riskAssessments} /> : null}
          {analysis.publicDocumentChecks ? <PublicDocumentCheckSection documents={analysis.publicDocumentChecks} /> : null}
        </div>

        <div className={groupClass('action')} data-group="action">
          {analysis.stageChecklists ? <StageChecklistTimeline stages={analysis.stageChecklists} /> : null}
          <Checklist items={analysis.checklist} />
          {analysis.questionsByTarget ? <QuestionsByTargetSection questions={analysis.questionsByTarget} /> : null}
          <DisclaimerBox />
        </div>

        <div className="print-hidden mt-8 flex justify-center">
          <ButtonLink to="/" variant="primary">
            다른 계약서 분석하기
          </ButtonLink>
        </div>
      </ReportLayout>

      <ChatWidget analysis={analysis} />
    </main>
  );
}
