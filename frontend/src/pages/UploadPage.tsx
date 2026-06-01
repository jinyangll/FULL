import {
  ArrowRight,
  Check,
  CheckCircle2,
  Clock3,
  FileCheck2,
  FileSearch,
  FileText,
  FileUp,
  HelpCircle,
  SearchCheck,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react';
import { useState } from 'react';
import { Button } from '../components/common/Button';
import Header from '../components/layout/Header';
import FileUploader from '../components/upload/FileUploader';
import { useAnalyzeContract } from '../hooks/useAnalyzeContract';

const heroFeatures = [
  { title: '전세가율·보증금 리스크', icon: FileText },
  { title: '등기부등본·권리관계 확인', icon: FileUp },
  { title: '임대인 체납·신원 점검', icon: Clock3 },
  { title: '특약·원상복구 조항 분석', icon: ShieldCheck },
];

const uploadInfo = [
  { title: '계약서 기반 분석', description: '본문·특약 확인', icon: FileText },
  { title: '공적서류 확인 분리', description: '추가 자료 안내', icon: FileSearch },
  { title: '참고용 리포트 생성', description: '체크리스트형', icon: FileCheck2 },
];

const trustItems = [
  {
    title: '계약서에서 확인할 항목',
    description: '보증금, 계약 기간, 특약, 원상복구, 중도 해지 조건을 먼저 정리합니다.',
    icon: FileText,
  },
  {
    title: '공적 서류로 확인할 항목',
    description: '등기부등본, 건축물대장, 전입세대 열람, 미납 국세 열람이 필요한 항목을 안내합니다.',
    icon: ShieldCheck,
  },
  {
    title: '전문가에게 물어볼 질문 정리',
    description: '임대인, 중개인, 법률 전문가에게 확인해야 할 질문을 함께 제공합니다.',
    icon: HelpCircle,
  },
];

const processSteps = [
  {
    title: '계약서 업로드',
    description: '전월세·임대차 계약서 PDF, JPG, PNG 파일을 선택합니다.',
    icon: FileUp,
  },
  {
    title: '계약서·공적서류 기반 점검',
    description: '전세가율, 권리관계, 체납, 특약 등 계약 전 확인할 항목을 자료별로 구분합니다.',
    icon: SearchCheck,
  },
  {
    title: '리포트 확인',
    description: '위험도, 확인 자료, 추가 질문, 체크리스트를 한눈에 확인합니다.',
    icon: FileCheck2,
  },
];

const reportBullets = [
  '계약서 확인: 보증금, 월세, 계약기간, 관리비, 특약',
  '권리관계 확인: 등기부등본, 신탁등기, 근저당',
  '건축물 확인: 건축물대장, 위반건축물 여부',
  '세금 확인: 미납 국세·지방세 열람',
  '입주 후 절차: 전입신고, 확정일자, 반환보증',
];

const cautionItems = [
  {
    title: '등기부등본은 계약 전, 잔금 전 각각 확인',
    description: '소유자, 신탁등기, 근저당, 가압류 등 권리관계가 바뀌지 않았는지 확인하세요.',
  },
  {
    title: '건축물대장으로 위반건축물 여부 확인',
    description: '용도 불일치, 불법 증축, 위반건축물 표시가 있는지 확인하세요.',
  },
  {
    title: '임대인의 미납 국세·지방세 열람 가능 여부 확인',
    description: '체납이 있으면 보증금 회수에 영향을 줄 수 있으므로 열람 협조를 요청하세요.',
  },
  {
    title: '신탁등기 또는 근저당이 있는 경우 계약 권한자 확인',
    description: '권한 없는 임대인과 계약하지 않도록 실제 계약 권한자를 확인하세요.',
  },
  {
    title: '보증보험 가입 가능 여부 확인',
    description: '전세가율이 높거나 권리관계가 복잡하면 보증보험 가입 가능성을 먼저 확인하세요.',
  },
  {
    title: '잔금 후 권리 변동 금지 특약 포함 여부 확인',
    description: '잔금 지급 이후 근저당 설정 등 권리 변동을 막는 특약이 있는지 확인하세요.',
  },
];

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const { start } = useAnalyzeContract();

  return (
    <>
      <Header />
      <main>
        <section
          id="top"
          className="scroll-mt-24 bg-[radial-gradient(circle_at_24%_18%,rgba(96,165,250,0.20),transparent_26rem),linear-gradient(135deg,#0f172a_0%,#0b2a55_48%,#082145_100%)]"
        >
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-14 sm:px-6 sm:py-20 lg:grid-cols-[minmax(0,1fr)_460px] lg:gap-16 lg:py-24">
            <div className="text-white">
              <span className="inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-bold text-slate-100 shadow-sm backdrop-blur">
                계약서·공적서류 기반 전월세 점검
              </span>

              <h1 className="mt-8 max-w-2xl break-keep text-[42px] font-bold leading-[1.12] tracking-normal sm:text-6xl lg:text-[64px]">
                전월세 계약 전
                <br />
                9가지 위험 요소를
                <br />
                먼저 확인하세요
              </h1>

              <p className="mt-6 max-w-2xl break-keep text-base leading-8 text-slate-200 sm:text-lg">
                보증금, 권리관계, 신탁등기, 체납, 특약 조항까지 전월세 계약 전 확인해야 할 9가지 위험 요소를
                정리해 드립니다.
              </p>

              <div className="mt-8 grid max-w-2xl gap-4 border-t border-white/10 pt-6 sm:grid-cols-2">
                {heroFeatures.map((feature) => {
                  const Icon = feature.icon;
                  return (
                    <div key={feature.title} className="flex items-center gap-3 text-base font-semibold text-slate-100">
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/10">
                        <Icon size={18} aria-hidden="true" />
                      </span>
                      <span className="break-keep">{feature.title}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div id="upload" className="scroll-mt-28 rounded-2xl bg-white p-6 shadow-[0_30px_90px_rgba(0,0,0,0.28)]">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-normal text-brand">전월세 계약서 업로드</h2>
                <p className="break-keep text-sm leading-6 text-brand-muted">
                  계약서 파일을 올리면 9가지 전월세 리스크 기준으로 점검 리포트를 생성합니다.
                </p>
              </div>

              <div className="mt-6">
                <FileUploader files={files} onChange={setFiles} />
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {uploadInfo.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="rounded-2xl bg-slate-50 p-3">
                      <div className="flex items-start gap-2">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-brand">
                          <Icon size={15} aria-hidden="true" />
                        </span>
                        <div>
                          <p className="text-xs font-bold text-brand">{item.title}</p>
                          <p className="mt-0.5 text-xs text-brand-muted">{item.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <Button
                type="button"
                className={`mt-6 w-full py-3.5 ${files.length > 0 ? 'shadow-lg shadow-slate-900/15' : 'bg-slate-100 text-slate-500'}`}
                disabled={files.length === 0}
                onClick={() => {
                  if (files.length > 0) {
                    start(files);
                  }
                }}
              >
                분석 시작하기
                <ArrowRight size={18} aria-hidden="true" />
              </Button>

              <p className="mt-4 break-keep text-center text-xs leading-5 text-brand-muted">
                업로드 파일은 현재 세션에서만 사용되며, 분석 흐름에 맞춰 임시로 처리돼요.
              </p>
            </div>
          </div>
        </section>

        <section id="service-intro" className="scroll-mt-24 bg-white px-5 py-14 sm:px-6 sm:py-16">
          <div className="mx-auto max-w-6xl">
            <div className="text-center">
              <h2 className="text-3xl font-bold tracking-normal text-brand">계약 전, 무엇을 확인해야 할까요?</h2>
              <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">
                계약서만으로 판단하기 어려운 항목은 공적 서류와 함께 확인해야 합니다.
              </p>
            </div>

            <div className="mt-8 grid gap-6 md:grid-cols-3">
              {trustItems.map((item) => {
                const Icon = item.icon;
                return (
                  <article
                    key={item.title}
                    className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_18px_45px_rgba(15,23,42,0.06)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_60px_rgba(15,23,42,0.10)]"
                  >
                    <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-brand-accent">
                      <Icon size={22} aria-hidden="true" />
                    </div>
                    <h3 className="break-keep text-base font-bold text-brand">{item.title}</h3>
                    <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{item.description}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="analysis-process" className="scroll-mt-24 bg-slate-50 px-5 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto max-w-6xl">
            <div className="text-center">
              <p className="text-sm font-bold text-brand-accent">분석 프로세스</p>
              <h2 className="mt-3 text-3xl font-bold tracking-normal text-brand">분석은 이렇게 진행돼요</h2>
              <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">
                업로드부터 리포트 확인까지 필요한 핵심 과정을 간단하게 보여드립니다.
              </p>
            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-[1fr_auto_1fr_auto_1fr] lg:items-center">
              {processSteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.title} className="contents">
                    <article className="min-h-44 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
                      <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand text-sm font-bold text-white">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      <div className="mt-6 flex items-start gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-100 text-brand">
                          <Icon size={22} aria-hidden="true" />
                        </div>
                        <div>
                          <h3 className="font-bold text-brand">{step.title}</h3>
                          <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{step.description}</p>
                        </div>
                      </div>
                    </article>
                    {index < processSteps.length - 1 ? (
                      <div className="hidden text-slate-300 lg:block" aria-hidden="true">
                        →
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section id="report-preview" className="scroll-mt-24 bg-white px-5 py-16 sm:px-6 sm:py-20">
          <div className="mx-auto grid max-w-6xl gap-10 rounded-3xl bg-slate-50 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] sm:p-9 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <p className="text-sm font-bold text-brand-accent">리포트 예시</p>
              <h2 className="mt-3 max-w-lg break-keep text-3xl font-bold leading-tight tracking-normal text-brand">
                리포트에서는 이런 항목을 확인할 수 있어요
              </h2>
              <p className="mt-4 break-keep text-sm leading-7 text-brand-muted">
                계약서만으로 판단 가능한 항목과 등기부등본·건축물대장·세금 열람이 필요한 항목을 구분해
                보여드립니다.
              </p>

              <ul className="mt-6 space-y-3">
                {reportBullets.map((item) => (
                  <li key={item} className="flex gap-3 text-sm font-semibold leading-6 text-brand">
                    <CheckCircle2 className="mt-0.5 shrink-0 text-brand-accent" size={17} aria-hidden="true" />
                    <span className="break-keep">{item}</span>
                  </li>
                ))}
              </ul>

              <a
                href="#report-preview-card"
                className="mt-8 inline-flex items-center justify-center gap-2 rounded-xl bg-brand px-5 py-3 text-sm font-bold text-white shadow-sm shadow-slate-900/15 transition hover:bg-brand-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2"
              >
                리포트 예시 더 보기
                <ArrowRight size={17} aria-hidden="true" />
              </a>
            </div>

            <div
              id="report-preview-card"
              className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_20px_60px_rgba(15,23,42,0.14)]"
            >
              <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-5 py-3">
                <span className="h-2.5 w-2.5 rounded-full bg-red-300" />
                <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
              </div>
              <div className="space-y-6 p-5 sm:p-6">
                <div>
                  <p className="text-xs font-bold text-brand-muted">분석 리포트</p>
                  <h3 className="mt-2 text-xl font-bold text-brand">계약서·공적서류 기반 점검</h3>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    {[
                      { label: '높음', count: '2건', className: 'bg-red-50 text-red-800' },
                      { label: '보통', count: '4건', className: 'bg-amber-50 text-amber-800' },
                      { label: '낮음', count: '3건', className: 'bg-blue-50 text-blue-800' },
                    ].map((item) => (
                      <div key={item.label} className={`rounded-xl p-4 ${item.className}`}>
                        <p className="text-xs font-bold">위험 {item.label}</p>
                        <p className="mt-1 text-lg font-bold">{item.count}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-sm font-bold text-brand">문서별 비교 분석</p>
                  <div className="mt-3 space-y-3">
                    {[
                      {
                        level: '높음',
                        title: '전세가율 과다',
                        source: '계약서 + 실거래가',
                        text: '보증금과 주변 실거래가 비교가 필요합니다.',
                      },
                      {
                        level: '높음',
                        title: '신탁등기 권리관계',
                        source: '등기부등본',
                        text: '신탁 여부와 계약 권한자를 확인해야 합니다.',
                      },
                      {
                        level: '보통',
                        title: '임대인 체납',
                        source: '미납 국세 열람',
                        text: '체납 여부가 보증금 회수에 영향을 줄 수 있습니다.',
                      },
                      {
                        level: '보통',
                        title: '잔금 후 권리 변동',
                        source: '계약서 특약',
                        text: '권리 변동 금지 특약 포함 여부를 확인하세요.',
                      },
                      {
                        level: '낮음',
                        title: '건축물 적법성',
                        source: '건축물대장',
                        text: '위반건축물 여부를 확인하세요.',
                      },
                    ].map((item) => (
                      <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-4">
                        <div className="flex items-center justify-between gap-3">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                              item.level === '높음'
                                ? 'bg-red-50 text-red-700'
                                : item.level === '보통'
                                  ? 'bg-amber-50 text-amber-700'
                                  : 'bg-blue-50 text-blue-700'
                            }`}
                          >
                            {item.level}
                          </span>
                          <button type="button" className="text-xs font-bold text-brand-accent">
                            자세히 보기
                          </button>
                        </div>
                        <p className="mt-2 text-sm font-bold text-brand">{item.title}</p>
                        <p className="mt-1 text-xs font-bold text-brand-accent">확인 자료: {item.source}</p>
                        <p className="mt-1 break-keep text-xs leading-5 text-brand-muted">{item.text}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-bold text-brand">체크리스트</p>
                  <div className="mt-3 flex items-start gap-2 text-xs font-semibold text-brand-muted">
                    <Check className="mt-0.5 shrink-0 text-emerald-600" size={15} aria-hidden="true" />
                    <span>계약 당일 등기부등본과 계약서상 임대인 일치 여부</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="disclaimer" className="scroll-mt-24 bg-slate-50 px-5 py-14 sm:px-6 sm:py-16">
          <div className="mx-auto max-w-6xl">
            <div className="mx-auto max-w-3xl text-center">
              <p className="text-sm font-bold text-brand-accent">주의사항</p>
              <h2 className="mt-3 text-3xl font-bold tracking-normal text-brand">
                AI 리포트만으로 계약을 결정하면 안 됩니다
              </h2>
              <p className="mt-3 break-keep text-sm leading-7 text-brand-muted">
                본 서비스는 계약 전 확인해야 할 위험 요소를 정리하는 참고 도구입니다. 실제 계약 전에는
                등기부등본, 건축물대장, 미납 국세, 전입세대 열람 등 최신 공적 자료를 반드시 확인해야 합니다.
              </p>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {cautionItems.map((item) => (
                <article
                  key={item.title}
                  className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-brand-accent">
                      <Check size={16} aria-hidden="true" />
                    </span>
                    <div>
                      <h3 className="font-bold text-brand">{item.title}</h3>
                      <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{item.description}</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-white px-5 py-12 sm:px-6">
          <div className="mx-auto flex max-w-6xl gap-4 rounded-2xl border border-amber-200 bg-amber-50 px-6 py-6 text-amber-950">
            <TriangleAlert className="mt-0.5 shrink-0" size={22} aria-hidden="true" />
            <p className="break-keep text-sm font-semibold leading-7">
              본 AI 분석 결과는 법적 효력이 없으며 참고용입니다. 보증금, 권리관계, 특약, 체납 여부 등 중요한
              사항은 반드시 공적 서류와 실제 계약 조건을 확인하고, 필요 시 공인중개사 또는 법률 전문가와
              상담하십시오.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}
