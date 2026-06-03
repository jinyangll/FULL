import { ArrowRight, MessageSquareText } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageHero from '../components/marketing/PageHero';
import ReportPreviewMock from '../components/marketing/ReportPreviewMock';

const reportSections = [
  {
    title: '리포트 상단 예시',
    description: '전월세 계약 사전 점검 리포트, 분석 범위, 참고용 리포트 배지를 먼저 보여줍니다.',
  },
  {
    title: '위험도 요약',
    description: '고위험, 주의, 확인 필요, 낮음 상태를 한눈에 비교합니다.',
  },
  {
    title: '계약 기본정보',
    description: '계약 유형, 임대인/임차인, 보증금, 월세, 계약기간, 관리비를 정리합니다.',
  },
  {
    title: '문서별 비교 분석',
    description: '계약서에서 확인된 항목과 외부 서류가 필요한 항목을 구분해 보여줍니다.',
  },
  {
    title: '추가 확인 서류',
    description: '등기부등본, 건축물대장, 전입세대확인서, 세금 열람 등 필요한 자료를 안내합니다.',
  },
  {
    title: '최종 코멘트',
    description: '현재 자료 기준 판단과 계약 전 추가 확인해야 할 행동을 요약합니다.',
  },
];

const questionGroups = [
  {
    title: '임대인에게 물어볼 질문',
    questions: ['미납 세금 열람에 동의하나요?', '잔금 전까지 새로운 근저당을 설정하지 않는 특약에 동의하나요?'],
  },
  {
    title: '중개인에게 물어볼 질문',
    questions: ['선순위 보증금 총액을 확인했나요?', '등기부등본 갑구·을구에 위험 권리가 없나요?'],
  },
  {
    title: '전문가에게 확인할 질문',
    questions: ['신탁등기 물건에서 계약 권한이 적법한가요?', '원상복구 특약이 임차인에게 과도하게 불리한가요?'],
  },
];

export default function ReportPreviewPage() {
  return (
    <main>
      <PageHero
        eyebrow="리포트 예시"
        title="리포트에서는 이런 정보를 확인할 수 있어요"
        description="계약서 분석 결과와 추가 확인이 필요한 공적서류를 한눈에 볼 수 있도록 정리합니다."
      >
        <Link
          to="/#upload"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-blue-950/20 transition hover:bg-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-200 focus-visible:ring-offset-2 focus-visible:ring-offset-[#061a36]"
        >
          계약서 분석 시작하기
          <ArrowRight size={17} aria-hidden="true" />
        </Link>
      </PageHero>

      <section className="px-5 py-14 sm:px-6 sm:py-16">
        <div className="mx-auto max-w-6xl">
          <ReportPreviewMock />
        </div>
      </section>

      <section className="bg-slate-50 px-5 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">리포트 구성</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              실제 결과 페이지의 구조를 미리 확인하세요
            </h2>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {reportSections.map((section) => (
              <article key={section.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-bold text-brand">{section.title}</h3>
                <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{section.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-14 sm:px-6 sm:py-16">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">질문 리스트 예시</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              계약 전 누구에게 무엇을 확인할지 정리합니다
            </h2>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-3">
            {questionGroups.map((group) => (
              <article key={group.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
                <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-brand">
                  <MessageSquareText size={21} aria-hidden="true" />
                </div>
                <h3 className="font-bold text-brand">{group.title}</h3>
                <ul className="mt-4 space-y-3">
                  {group.questions.map((question) => (
                    <li key={question} className="break-keep text-sm leading-6 text-brand-muted">
                      {question}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
