import type { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export default function FeatureCard({ title, description, icon: Icon }: FeatureCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 text-brand">
        <Icon size={21} aria-hidden="true" />
      </div>
      <h2 className="break-keep text-lg font-bold text-brand">{title}</h2>
      <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">{description}</p>
    </article>
  );
}
