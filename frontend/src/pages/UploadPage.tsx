import {
  ArrowRight,
  FileCheck2,
  FileSearch,
  FileText,
  Landmark,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import HeroMockup from '../components/marketing/HeroMockup';
import FileUploader from '../components/upload/FileUploader';
import { useAnalyzeContract } from '../hooks/useAnalyzeContract';

const heroFeatures = [
  {
    title: '계약서 특약 분석',
    description: '보증금, 기간, 특약, 원상복구, 중도 해지 조항까지 확인합니다.',
    icon: FileCheck2,
  },
  {
    title: '공적서류 확인 안내',
    description: '등기부등본, 건축물대장, 세금 열람이 필요한 항목을 알려줍니다.',
    icon: Landmark,
  },
  {
    title: '위험도 우선순위 정리',
    description: '고위험부터 확인 필요 항목까지 우선순위를 정리해 드립니다.',
    icon: ShieldCheck,
  },
  {
    title: '임대인·중개인 질문 제공',
    description: '누구에게 무엇을 물어봐야 하는지 구체적인 질문 리스트를 제공합니다.',
    icon: Users,
  },
];

const uploadInfo = [
  { title: '계약서 기반 분석', icon: FileText },
  { title: '추가 서류 필요 항목 분류', icon: FileSearch },
  { title: '참고용 리포트 생성', icon: FileCheck2 },
];

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const { start } = useAnalyzeContract();

  return (
    <main>
      <section
        id="top"
        className="relative overflow-visible bg-[radial-gradient(circle_at_65%_34%,rgba(59,130,246,0.22),transparent_22rem),linear-gradient(135deg,#071A35_0%,#08264A_48%,#06182F_100%)]"
      >
        <div className="absolute inset-x-0 top-0 h-px bg-white/10" aria-hidden="true" />
        <div className="mx-auto grid max-w-[1360px] items-center gap-12 px-5 pb-24 pt-14 sm:px-6 sm:pt-20 lg:min-h-[760px] lg:grid-cols-[0.76fr_1.04fr] lg:gap-14 lg:pb-44 lg:pt-20">
          <div className="text-white">
            <span className="inline-flex rounded-full border border-blue-300/20 bg-blue-400/10 px-4 py-2 text-sm font-bold text-blue-100 shadow-sm">
              전월세 계약 사전 점검 MVP
            </span>

            <h1 className="mt-8 max-w-2xl break-keep text-[42px] font-bold leading-[1.12] tracking-normal sm:text-6xl lg:text-[66px]">
              전월세 계약서<span className="text-[0.6em]">,</span>
              <br />
              서명 전에 먼저
              <br />
              점검하세요
            </h1>

            <p className="mt-6 max-w-xl break-keep text-base leading-8 text-slate-200 sm:text-lg">
              계약서에서 확인 가능한 항목과{' '}
              <br className="hidden sm:block" />
              등기부등본·건축물대장·세금 열람처럼{' '}
              <br className="hidden sm:block" />
              추가 확인이 필요한 항목을 나눠{' '}
              <br className="hidden sm:block" />
              리포트로 정리합니다.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <a
                href="#upload"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-500 px-6 py-4 text-base font-bold text-white shadow-lg shadow-blue-950/25 transition hover:bg-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-200 focus-visible:ring-offset-2 focus-visible:ring-offset-[#061a36]"
              >
                계약서 분석 시작하기
                <ArrowRight size={19} aria-hidden="true" />
              </a>
              <Link
                to="/report-preview"
                className="inline-flex items-center justify-center rounded-xl border border-white/30 px-6 py-4 text-base font-bold text-white transition hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-200 focus-visible:ring-offset-2 focus-visible:ring-offset-[#061a36]"
              >
                리포트 예시 보기
              </Link>
            </div>
          </div>

          <HeroMockup />
        </div>

        <div className="relative z-10 mx-auto max-w-[1360px] px-5 sm:px-6 lg:absolute lg:inset-x-0 lg:bottom-0 lg:translate-y-1/2">
          <div className="-mb-16 grid overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-[0_28px_80px_rgba(15,23,42,0.20)] md:grid-cols-2 lg:mb-0 lg:grid-cols-4">
            {heroFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <article
                  key={feature.title}
                  className={`flex gap-4 p-6 lg:px-7 lg:py-8 ${index > 0 ? 'border-t border-slate-200 md:border-l md:border-t-0' : ''} ${index === 2 ? 'md:border-l-0 lg:border-l' : ''}`}
                >
                  <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                    <Icon size={24} aria-hidden="true" />
                  </span>
                  <div>
                    <h2 className="break-keep text-base font-bold text-brand">{feature.title}</h2>
                    <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">{feature.description}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section id="upload" className="scroll-mt-28 bg-white px-5 pb-14 pt-28 sm:px-6 sm:pb-16 lg:pt-48">
        <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[0.78fr_1.22fr] lg:items-start">
          <div>
            <p className="text-sm font-bold text-brand-accent">분석 시작</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              전월세 계약서 업로드
            </h2>
            <p className="mt-4 break-keep text-sm leading-7 text-brand-muted sm:text-base">
              PDF, JPG, PNG 계약서를 올리면 계약서에서 확인 가능한 항목과 추가 자료가 필요한 항목을 나눠
              분석합니다.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {uploadInfo.map((item) => {
                const Icon = item.icon;
                return (
                  <span
                    key={item.title}
                    className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-brand"
                  >
                    <Icon size={14} aria-hidden="true" />
                    {item.title}
                  </span>
                );
              })}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card sm:p-6">
            <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-bold text-emerald-700">
              <ShieldCheck size={14} aria-hidden="true" />
              서버 무저장 · 분석 결과는 전달 즉시 파기됩니다
            </p>
            <FileUploader files={files} onChange={setFiles} />
            <Button
              type="button"
              className="mt-6 w-full py-3.5"
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
              업로드한 파일과 분석 결과는 서버에 저장하지 않으며, 결과는 계약 전 참고용으로 제공됩니다.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
