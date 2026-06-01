import { AlertTriangle, Check, FileSearch } from 'lucide-react';
import PageHero from '../components/marketing/PageHero';

const documents = [
  {
    name: '등기부등본',
    checks: '소유자, 근저당, 압류, 가압류, 신탁등기',
    risk: '권리관계, 신탁등기, 잔금 후 권리 변동',
    timing: '계약 전, 계약 당일, 잔금 직전',
  },
  {
    name: '건축물대장',
    checks: '위반건축물 여부, 용도, 면적, 층·호수',
    risk: '건축물 적법성, 보증보험 가입 제한',
    timing: '계약 직전',
  },
  {
    name: '전입세대확인서',
    checks: '선순위 세입자 존재 여부, 다가구 선순위 보증금',
    risk: '다가구 공동 담보, 선순위 임차보증금',
    timing: '계약 직전, 잔금 직전',
  },
  {
    name: '미납 국세·지방세 열람',
    checks: '임대인의 체납 여부, 납세증명서 또는 열람 가능 여부',
    risk: '임대인 체납, 보증금 회수 위험',
    timing: '계약 직전, 잔금 직전',
  },
  {
    name: '신탁원부',
    checks: '수탁자, 실제 계약 권한자, 신탁회사 동의',
    risk: '신탁등기 권리관계',
    timing: '신탁등기 표시가 있을 때 즉시',
  },
  {
    name: '중개대상물 확인·설명서',
    checks: '선순위 권리관계, 관리비, 체납세금 설명',
    risk: '권리관계, 관리비, 선순위 보증금',
    timing: '계약서 작성 전',
  },
  {
    name: '실거래가 공개시스템 / 안심전세 App',
    checks: '최근 매매 실거래가, 전세가율, 보증 가능 여부',
    risk: '전세가율 과다, 보증보험 가입 제한',
    timing: '물건 탐색, 계약 직전',
  },
];

const cautions = [
  '등기부등본은 계약 전과 잔금 직전 각각 확인',
  '신탁등기 또는 근저당이 있으면 계약 권한자 확인',
  '다가구는 선순위 임차보증금 확인',
  '미납 세금 확인',
  '특약에 잔금 후 권리 변동 금지 문구 포함',
  '전입신고와 확정일자는 입주 직후 진행',
];

export default function GuidePage() {
  return (
    <main>
      <PageHero
        eyebrow="이용 안내"
        title="AI 리포트만으로 계약을 결정하면 안 됩니다"
        description="HERO는 계약 전 확인해야 할 항목을 정리하는 참고 도구입니다. 실제 계약 전에는 공적서류와 전문가 확인이 필요합니다."
      />

      <section className="px-5 py-14 sm:px-6 sm:py-16">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">반드시 확인할 공적서류</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              서류별 확인 내용과 시점을 나눠 봅니다
            </h2>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-2">
            {documents.map((document) => (
              <article key={document.name} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-start gap-4">
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-brand">
                    <FileSearch size={21} aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="font-bold text-brand">{document.name}</h3>
                    <dl className="mt-3 space-y-2 text-sm leading-6">
                      <div>
                        <dt className="font-bold text-brand-muted">무엇을 확인하나요</dt>
                        <dd className="break-keep text-brand">{document.checks}</dd>
                      </div>
                      <div>
                        <dt className="font-bold text-brand-muted">연결되는 리스크</dt>
                        <dd className="break-keep text-brand">{document.risk}</dd>
                      </div>
                      <div>
                        <dt className="font-bold text-brand-muted">언제 확인하나요</dt>
                        <dd className="break-keep text-brand">{document.timing}</dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-slate-50 px-5 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <p className="text-sm font-bold text-brand-accent">계약 전 주의사항</p>
            <h2 className="mt-3 break-keep text-3xl font-bold tracking-normal text-brand sm:text-4xl">
              계약 직전과 입주 직후에 다시 확인하세요
            </h2>
          </div>
          <div className="mt-9 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {cautions.map((item) => (
              <article key={item} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-brand-accent">
                    <Check size={16} aria-hidden="true" />
                  </span>
                  <p className="break-keep text-sm font-bold leading-6 text-brand">{item}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-14 sm:px-6">
        <div className="mx-auto flex max-w-6xl gap-4 rounded-2xl border border-amber-200 bg-amber-50 px-6 py-6 text-amber-950">
          <AlertTriangle className="mt-0.5 shrink-0" size={22} aria-hidden="true" />
          <p className="break-keep text-sm font-semibold leading-7">
            HERO 분석 결과는 법적 효력이 없으며 참고용입니다. 보증금, 권리관계, 특약, 체납 여부 등 중요한
            사항은 반드시 공적서류와 실제 계약 조건을 확인하고, 필요 시 공인중개사 또는 법률 전문가와
            상담하십시오.
          </p>
        </div>
      </section>
    </main>
  );
}
