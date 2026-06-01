import { CheckCircle2, FileText, Shield } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

const navItems = [
  { label: '서비스 소개', to: '/service' },
  { label: '분석 프로세스', to: '/process' },
  { label: '리포트 예시', to: '/report-preview' },
  { label: '이용 안내', to: '/guide' },
];

export default function Header() {
  return (
    <header className="print-hidden sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-xl">
      <div className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-5 sm:px-6">
        <Link
          to="/"
          className="flex items-center gap-3 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2"
          aria-label="HERO 홈"
        >
          <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-brand text-white shadow-sm shadow-slate-900/20">
            <Shield size={34} strokeWidth={2.1} aria-hidden="true" />
            <FileText className="absolute" size={17} strokeWidth={2.2} aria-hidden="true" />
            <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full border-2 border-white bg-blue-500 text-white">
              <CheckCircle2 size={13} strokeWidth={2.6} aria-hidden="true" />
            </span>
          </div>
          <div>
            <p className="text-2xl font-bold leading-none tracking-normal text-brand">HERO</p>
            <p className="mt-1 text-xs font-semibold text-brand-muted">전월세 계약 리스크 분석</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-7 lg:flex" aria-label="주요 섹션">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) =>
                `text-sm font-bold transition hover:text-brand-accent focus:outline-none focus-visible:rounded-md focus-visible:ring-2 focus-visible:ring-brand-accent ${
                  isActive ? 'text-brand-accent' : 'text-brand'
                }`
              }
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <Link
          className="inline-flex items-center justify-center rounded-xl bg-brand px-4 py-2.5 text-sm font-bold text-white shadow-sm shadow-slate-900/15 transition hover:bg-brand-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2 sm:px-5"
          to="/#upload"
        >
          계약서 분석 시작하기
        </Link>
      </div>
    </header>
  );
}
