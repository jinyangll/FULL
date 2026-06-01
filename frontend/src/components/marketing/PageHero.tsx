import type { ReactNode } from 'react';

interface PageHeroProps {
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
}

export default function PageHero({ eyebrow, title, description, children }: PageHeroProps) {
  return (
    <section className="bg-[#061a36] px-5 py-14 text-white sm:px-6 sm:py-20">
      <div className="mx-auto max-w-6xl">
        <p className="text-sm font-bold text-blue-200">{eyebrow}</p>
        <h1 className="mt-4 max-w-3xl break-keep text-4xl font-bold leading-tight tracking-normal sm:text-5xl">
          {title}
        </h1>
        <p className="mt-5 max-w-3xl break-keep text-base leading-8 text-slate-200 sm:text-lg">{description}</p>
        {children ? <div className="mt-8">{children}</div> : null}
      </div>
    </section>
  );
}
