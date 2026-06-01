import { ClipboardCheck, FileSearch, FileText, FileUp, ListChecks, SearchCheck } from 'lucide-react';
import PageHero from '../components/marketing/PageHero';

const processSteps = [
  {
    title: '문서 업로드',
    description: '계약서 PDF/JPG/PNG를 업로드합니다. 관련 공적서류가 있으면 함께 업로드할 수 있습니다.',
    icon: FileUp,
  },
  {
    title: '문서 유형 확인',
    description: '계약서인지, 등기부등본인지, 건축물대장인지 구분하고 지원하지 않는 문서는 안내합니다.',
    icon: FileSearch,
  },
  {
    title: '계약서 정보 추출',
    description: '임대인/임차인, 주소, 보증금/월세, 계약기간, 관리비, 특약을 구조화합니다.',
    icon: FileText,
  },
  {
    title: '리스크 분류',
    description: '계약서에서 확인됨, 외부 서류 확인 필요, 조건부 해당, 현재 자료만으로 판단 불가로 나눕니다.',
    icon: ListChecks,
  },
  {
    title: '리포트 생성',
    description: '위험도 요약, 문서별 비교 분석, 추가 확인 서류, 질문 리스트, 단계별 체크리스트를 정리합니다.',
    icon: ClipboardCheck,
  },
];

const stageFlow = [
  {
    stage: '물건 탐색',
    items: ['실거래가 확인', '전세가율 확인', '안심전세 App 확인'],
  },
  {
    stage: '계약 직전',
    items: ['등기부등본 확인', '건축물대장 확인', '전입세대확인서 확인', '미납 국세·지방세 열람 가능 여부 확인'],
  },
  {
    stage: '계약서 작성',
    items: ['특약 확인', '원상복구 범위 확인', '담보권 설정금지 특약 확인'],
  },
  {
    stage: '계약 당일 / 잔금 직전',
    items: ['등기부등본 재확인', '임대인 신원 확인', '보증금 입금 계좌 확인'],
  },
  {
    stage: '입주 직후',
    items: ['전입신고', '확정일자', '보증보험 확인'],
  },
];

export default function ProcessPage() {
  return (
    <main>
      <PageHero
        eyebrow="분석 프로세스"
        title="분석은 이렇게 진행돼요"
        description="업로드부터 리포트 확인까지, HERO는 계약서와 추가 확인 자료를 구분해 단계별로 정리합니다."
      />

      <section className="px-5 py-14 sm:px-6 sm:py-16">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-5 lg:grid-cols-5">
            {processSteps.map((step, index) => {
              const Icon = step.icon;
              return (
                <article key={step.title} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-sm font-bold text-brand-accent">{String(index + 1).padStart(2, '0')}</span>
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-brand">
                      <Icon size={20} aria-hidden="true" />
                    </span>
                  </div>
                  <h2 className="mt-6 break-keep font-bold text-brand">{step.title}</h2>
                  <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{step.description}</p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="bg-slate-50 px-5 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">계약 단계별 체크 흐름</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              계약 전부터 입주 직후까지 확인합니다
            </h2>
          </div>
          <div className="mt-9 grid gap-4 md:grid-cols-2">
            {stageFlow.map((stage, index) => (
              <article key={stage.stage} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand text-sm font-bold text-white">
                    {index + 1}
                  </span>
                  <h3 className="font-bold text-brand">{stage.stage}</h3>
                </div>
                <ul className="mt-4 grid gap-2">
                  {stage.items.map((item) => (
                    <li key={item} className="flex items-start gap-3 break-keep text-sm leading-6 text-brand-muted">
                      <SearchCheck className="mt-0.5 shrink-0 text-brand-accent" size={16} aria-hidden="true" />
                      {item}
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
