const previewRows = [
  {
    title: '특약 조항 이상 여부',
    source: '계약서 본문 및 특약',
    status: '계약서에서 확인됨',
    action: '모호한 문구 수정 요청',
    tone: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  },
  {
    title: '신탁등기 권리관계',
    source: '등기부등본, 신탁원부',
    status: '외부 서류 확인 필요',
    action: '계약 권한자 확인',
    tone: 'border-blue-200 bg-blue-50 text-blue-800',
  },
  {
    title: '임대인 체납 여부',
    source: '미납 국세·지방세 열람',
    status: '현재 자료만으로 판단 불가',
    action: '열람 동의 또는 증빙 요청',
    tone: 'border-slate-300 bg-slate-50 text-slate-700',
  },
];

export default function ReportPreviewMock() {
  return (
    <div
      id="report-preview-card"
      className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_22px_70px_rgba(15,23,42,0.14)]"
    >
      <div className="border-b border-slate-200 bg-slate-50 px-5 py-4">
        <p className="text-xs font-bold text-brand-muted">HERO 리포트</p>
        <h2 className="mt-1 text-xl font-bold text-brand">현재 리포트가 확인한 범위</h2>
        <p className="mt-2 break-keep text-xs leading-5 text-brand-muted">
          계약서에서 확인한 내용과 공적서류가 필요한 항목을 분리해 표시합니다.
        </p>
      </div>
      <div className="space-y-5 p-5 sm:p-6">
        <div className="grid gap-3 sm:grid-cols-5">
          {[
            { label: '고위험', count: '2건', className: 'bg-red-50 text-red-800' },
            { label: '주의', count: '3건', className: 'bg-amber-50 text-amber-800' },
            { label: '확인 필요', count: '6건', className: 'bg-blue-50 text-blue-800' },
            { label: '판단 불가', count: '2건', className: 'bg-slate-100 text-slate-700' },
            { label: '낮음', count: '1건', className: 'bg-emerald-50 text-emerald-800' },
          ].map((item) => (
            <div key={item.label} className={`rounded-xl p-4 ${item.className}`}>
              <p className="text-xs font-bold">{item.label}</p>
              <p className="mt-1 text-lg font-bold">{item.count}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          {[
            ['계약 유형', '전세 임대차 계약'],
            ['임대인 / 임차인', 'OOO / OOO'],
            ['보증금', '100,000,000원'],
            ['월세', '없음'],
            ['계약기간', '2025.05.01 ~ 2027.04.30'],
            ['관리비', '100,000원'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs font-bold text-brand-muted">{label}</p>
              <p className="mt-1 break-keep text-sm font-bold text-brand">{value}</p>
            </div>
          ))}
        </div>

        <div>
          <p className="text-sm font-bold text-brand">문서별 비교 분석</p>
          <div className="mt-3 space-y-3">
            {previewRows.map((item) => (
              <div key={item.title} className="rounded-xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-bold text-brand">{item.title}</p>
                  <span className={`rounded-full border px-2.5 py-1 text-xs font-bold ${item.tone}`}>
                    {item.status}
                  </span>
                </div>
                <p className="mt-2 text-xs font-bold text-brand-accent">확인 자료: {item.source}</p>
                <p className="mt-1 break-keep text-xs font-semibold leading-5 text-brand-muted">행동: {item.action}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
