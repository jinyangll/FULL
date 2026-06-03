import { ArrowRight, CheckCircle2, FileText, Sparkles } from 'lucide-react';

const contractFields = [
  ['보증금', '100,000,000원'],
  ['월세', '500,000원'],
  ['계약기간', '2025.05.01 ~ 2027.04.30'],
  ['관리비', '100,000원'],
  ['특약사항', '있음'],
];

const analysisSteps = ['계약서 내용 추출', '리스크 항목 분류', '추가 서류 필요 항목 선별', '리포트 생성'];

const reportRiskStats = [
  { label: '고위험', value: '2건', className: 'bg-red-50 text-red-700' },
  { label: '주의', value: '3건', className: 'bg-amber-50 text-amber-700' },
  { label: '확인 필요', value: '6건', className: 'bg-blue-50 text-blue-700' },
];

const reportResultStats = [
  { label: '계약서에서 확인됨', value: '8건', className: 'bg-emerald-50 text-emerald-700' },
  { label: '외부 서류 확인 필요', value: '6건', className: 'bg-orange-50 text-orange-700' },
  { label: '조건부 해당', value: '2건', className: 'bg-amber-50 text-amber-700' },
];

export default function HeroMockup() {
  return (
    <div className="relative mx-auto min-w-0 w-full max-w-[780px] lg:justify-self-end">
      <div className="space-y-4 md:hidden" data-hero-mockup="mobile">
        <ReportCard />
      </div>

      <div
        className="relative hidden h-[560px] md:block lg:w-[700px] lg:max-w-none 2xl:w-[820px]"
        data-hero-mockup="desktop"
      >
        <div className="absolute left-2 top-[116px] z-20 w-[245px] -rotate-2 lg:left-0 lg:top-[100px] lg:w-[250px] 2xl:w-[285px]">
          <ContractCard />
        </div>

        <div className="absolute left-[270px] top-[238px] z-0 h-px w-[115px] border-t-2 border-dashed border-blue-200/70 lg:left-[262px] lg:w-[38px] 2xl:left-[300px] 2xl:w-[44px]" />
        <div className="absolute left-[418px] top-[238px] z-0 h-px w-[100px] border-t-2 border-dashed border-blue-200/70 lg:left-[380px] lg:w-[34px] 2xl:left-[424px] 2xl:w-[38px]" />
        <div className="absolute left-[382px] top-[278px] z-0 h-[72px] border-l-2 border-dashed border-blue-200/70 lg:left-[340px] 2xl:left-[384px]" />

        <div className="absolute left-[344px] top-[200px] z-30 flex h-20 w-20 items-center justify-center rounded-full border border-blue-300/40 bg-blue-500 text-white shadow-[0_0_0_18px_rgba(59,130,246,0.12),0_22px_45px_rgba(15,23,42,0.24)] lg:left-[300px] 2xl:left-[344px]">
          <Sparkles size={30} aria-hidden="true" />
        </div>
        <ArrowRight className="absolute left-[506px] top-[225px] z-10 text-blue-200 lg:left-[390px] 2xl:left-[454px]" size={28} aria-hidden="true" />

        <div className="absolute left-[300px] top-[364px] z-20 w-[215px] lg:left-[260px] lg:top-[352px] lg:w-[150px] 2xl:left-[292px] 2xl:w-[180px]">
          <AnalysisCard />
        </div>

        <div className="absolute right-0 top-[58px] z-10 w-[365px] lg:top-[44px] lg:w-[320px] 2xl:-right-4 2xl:w-[390px]">
          <ReportCard />
        </div>
      </div>
    </div>
  );
}

function ContractCard() {
  return (
    <div className="rounded-2xl border border-white/30 bg-white p-5 text-brand shadow-[0_28px_70px_rgba(0,0,0,0.30)]">
      <h2 className="text-base font-bold">전월세 계약서</h2>
      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div className="mx-auto h-40 w-40 rounded-lg border border-slate-200 bg-white p-3 shadow-inner">
          <div className="mb-3 flex items-center gap-2">
            <FileText size={16} className="text-slate-400" aria-hidden="true" />
            <div className="h-2 w-20 rounded-full bg-slate-300" />
          </div>
          {Array.from({ length: 9 }).map((_, index) => (
            <div
              key={index}
              className={`mb-2 h-1.5 rounded-full ${index % 3 === 0 ? 'bg-slate-300' : 'bg-slate-200'}`}
              style={{ width: `${index % 3 === 0 ? 86 : index % 3 === 1 ? 68 : 94}%` }}
            />
          ))}
        </div>
      </div>
      <dl className="mt-4 space-y-3 rounded-xl bg-slate-50 p-4">
        {contractFields.map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-3 text-xs">
            <dt className="font-semibold text-brand-muted">{label}</dt>
            <dd className="text-right font-bold text-brand">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function AnalysisCard() {
  return (
    <div className="rounded-2xl border border-white/30 bg-white/95 p-4 text-brand shadow-[0_18px_50px_rgba(0,0,0,0.22)] 2xl:p-5">
      <h2 className="text-base font-bold">AI 분석 중...</h2>
      <ul className="mt-4 space-y-3">
        {analysisSteps.map((step, index) => (
          <li key={step} className="flex items-center gap-2 text-[11px] font-semibold leading-4 text-brand 2xl:text-xs">
            <CheckCircle2 className={index < 3 ? 'text-blue-600' : 'text-slate-400'} size={16} aria-hidden="true" />
            <span>{step}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ReportCard() {
  return (
    <div className="rounded-2xl border border-white/30 bg-white p-5 text-brand shadow-[0_30px_80px_rgba(0,0,0,0.32)] lg:p-6">
      <h2 className="break-keep text-lg font-bold 2xl:text-2xl">전월세 계약 사전 점검 리포트</h2>
      <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-sm font-bold text-brand">위험도 요약</p>
        <div className="mt-3 grid grid-cols-3 gap-2">
          {reportRiskStats.map((item) => (
            <div key={item.label} className={`rounded-xl p-3 text-center 2xl:p-4 ${item.className}`}>
              <p className="whitespace-nowrap text-[11px] font-bold 2xl:text-xs">{item.label}</p>
              <p className="mt-1 text-2xl font-bold lg:text-3xl">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-sm font-bold text-brand">문서별 확인 결과</p>
        <div className="mt-3 space-y-2">
          {reportResultStats.map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3">
              <span className="text-xs font-bold text-brand lg:text-sm">{item.label}</span>
              <span className={`rounded-full px-3 py-1 text-xs font-bold ${item.className}`}>{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
