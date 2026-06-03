import type { ReactNode } from 'react';
import TableOfContents from './TableOfContents';

export default function ReportLayout({ children }: { children: ReactNode }) {
  return (
    <div className="report-layout grid gap-8 md:grid-cols-[200px_minmax(0,1fr)] xl:grid-cols-[220px_minmax(0,1fr)]">
      <TableOfContents />
      <div className="report-content min-w-0">{children}</div>
    </div>
  );
}
