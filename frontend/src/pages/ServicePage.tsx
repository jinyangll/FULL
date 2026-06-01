import { AlertTriangle, Building2, CircleHelp, FileText, ListChecks, Scale, ShieldCheck } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import FeatureCard from '../components/marketing/FeatureCard';
import PageHero from '../components/marketing/PageHero';

const problemItems = [
  '보증금 반환 조건을 놓칠 수 있음',
  '특약이 임차인에게 불리할 수 있음',
  '등기부등본상 근저당·신탁등기 여부를 별도로 확인해야 함',
  '건축물대장, 전입세대확인서, 세금 열람 등 여러 자료를 따로 봐야 함',
];

const heroWork = [
  '계약서 내용 추출',
  '계약 기본정보 요약',
  '특약·원상복구·중도해지 등 계약서 기반 리스크 분석',
  '외부 공적서류가 필요한 항목 분류',
  '질문 리스트 제공',
];

const notDoing = [
  '법률 자문을 제공하지 않습니다.',
  '계약 안전 여부를 확정 판단하지 않습니다.',
  '등기부등본이나 세금 자료를 자동으로 대신 발급하지 않습니다.',
  '확인이 필요한 항목은 추가 확인 필요로 표시합니다.',
];

const cards = [
  {
    title: '계약서에서 확인할 것',
    description: '보증금, 월세, 계약기간, 관리비, 특약, 원상복구, 중도 해지 조건을 계약서에서 먼저 확인합니다.',
    icon: FileText,
  },
  {
    title: '공적서류로 확인할 것',
    description: '등기부등본, 건축물대장, 전입세대확인서, 미납 국세·지방세 열람이 필요한 항목을 분리합니다.',
    icon: Building2,
  },
  {
    title: '계약 전 물어볼 것',
    description: '임대인, 중개인, 전문가에게 확인해야 할 질문을 대상별로 정리합니다.',
    icon: CircleHelp,
  },
];

export default function ServicePage() {
  return (
    <main>
      <PageHero
        eyebrow="서비스 소개"
        title="계약서만으로 판단하지 않아요"
        description="전월세 계약의 핵심 리스크는 계약서 한 장만으로는 모두 확인하기 어렵습니다. HERO는 계약서에서 확인 가능한 항목과 공적서류로 추가 확인해야 할 항목을 구분해 보여줍니다."
      />

      <section className="px-5 py-14 sm:px-6 sm:py-16">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-3">
          <InfoPanel title="사용자가 겪는 문제" items={problemItems} icon={AlertTriangle} />
          <InfoPanel title="HERO가 하는 일" items={heroWork} icon={ListChecks} />
          <InfoPanel title="HERO가 하지 않는 일" items={notDoing} icon={Scale} />
        </div>
      </section>

      <section className="bg-slate-50 px-5 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">분류 기준</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              계약 전 확인할 일을 세 갈래로 나눕니다
            </h2>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-3">
            {cards.map((card) => (
              <FeatureCard key={card.title} {...card} />
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-14 sm:px-6">
        <div className="mx-auto grid max-w-6xl gap-5 rounded-2xl border border-blue-100 bg-blue-50 p-6 sm:p-8 md:grid-cols-[auto_1fr]">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-brand-accent">
            <ShieldCheck size={24} aria-hidden="true" />
          </div>
          <div>
            <h2 className="break-keep text-2xl font-bold text-brand">브랜드 문장</h2>
            <p className="mt-3 break-keep text-base font-semibold leading-7 text-brand">
              계약서와 공적서류를 나눠 보고, 계약 전 위험 신호를 정리합니다.
            </p>
            <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
              계약서에서 확인 가능한 항목은 명확히 보여주고, 공적서류 확인이 필요한 항목은 추가 확인으로
              분리해 표시합니다.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

function InfoPanel({ title, items, icon: Icon }: { title: string; items: string[]; icon: LucideIcon }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-brand">
        <Icon size={21} aria-hidden="true" />
      </div>
      <h2 className="text-lg font-bold text-brand">{title}</h2>
      <ul className="mt-4 space-y-3">
        {items.map((item) => (
          <li key={item} className="break-keep text-sm leading-6 text-brand-muted">
            {item}
          </li>
        ))}
      </ul>
    </article>
  );
}
