import type { PublicDocumentCheck } from '../../types/analysis';
import Badge from '../common/Badge';
import Card from '../common/Card';
import SectionHeading from '../common/SectionHeading';

export default function PublicDocumentCheckSection({ documents }: { documents: PublicDocumentCheck[] }) {
  return (
    <section id="required-documents" className="print-section scroll-mt-8">
      <Card className="space-y-5">
        <div>
          <SectionHeading title="추가로 확인해야 할 공적서류" />
          <p className="mt-2 break-keep text-sm leading-6 text-brand-muted">
            {documents.length > 0
              ? '아래 공적서류를 추가로 확인하면 계약서만으로 판단하기 어려운 위험을 더 정확히 볼 수 있습니다.'
              : '필요한 공적서류를 모두 업로드하셨습니다. 추가로 확인할 서류가 없습니다.'}
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {documents.map((document) => (
            <article key={document.name} className="print-card rounded-2xl border border-slate-200 bg-white p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <h3 className="font-bold text-brand">{document.name}</h3>
                <Badge level={document.importance} />
              </div>
              <p className="mt-3 break-keep text-sm leading-6 text-brand-muted">{document.reason}</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <ListBlock title="확인 내용" items={document.checks} />
                <ListBlock title="연결 리스크" items={document.relatedRisks} />
              </div>
            </article>
          ))}
        </div>
      </Card>
    </section>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-bold text-brand-muted">{title}</p>
      <ul className="mt-2 space-y-1">
        {items.map((item) => (
          <li key={item} className="break-keep text-sm leading-6 text-brand">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
