import { useSearchParams } from 'react-router-dom';

const groups = [
  { tab: 'summary', label: '핵심 요약', hint: '최종 코멘트 · 위험도 · 확인 범위' },
  { tab: 'detail', label: '상세 분석', hint: '계약정보 · 문서별 분석 · 추가 서류' },
  { tab: 'action', label: '행동 가이드', hint: '체크리스트 · 질문 · 면책' },
] as const;

export default function TableOfContents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const active = searchParams.get('tab') ?? 'summary';

  const handleSelect = (tab: string) => {
    setSearchParams({ tab });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <aside className="print-hidden md:sticky md:top-24 md:self-start">
      <nav className="flex gap-2 overflow-x-auto rounded-2xl border border-slate-200 bg-white/90 p-2 shadow-sm backdrop-blur md:flex-col md:p-3">
        <p className="hidden px-3 pb-2 pt-1 text-xs font-bold text-brand-muted md:block">리포트 목차</p>
        {groups.map((group) => {
          const isActive = active === group.tab;
          return (
            <button
              key={group.tab}
              type="button"
              aria-current={isActive ? 'page' : undefined}
              onClick={() => handleSelect(group.tab)}
              className={`whitespace-nowrap rounded-xl px-4 py-2 text-left text-sm font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent md:whitespace-normal ${
                isActive
                  ? 'bg-brand-accent/10 text-brand-accent ring-1 ring-brand-accent/20'
                  : 'text-brand-muted hover:bg-slate-100 hover:text-brand'
              }`}
            >
              {group.label}
              <span className="hidden text-xs font-normal text-brand-muted md:mt-0.5 md:block">{group.hint}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
