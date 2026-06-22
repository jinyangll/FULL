import { useEffect, useMemo, useRef } from 'react';
import type { RiskAssessment } from '../../types/analysis';
import { buildHighlightSegments, LEVEL_MARK_CLASS, type HighlightInput } from '../../lib/highlight';

export default function ContractViewer({
  text,
  risks,
  activeRiskId,
}: {
  text: string;
  risks: RiskAssessment[];
  activeRiskId: string | null;
}) {
  const highlights = useMemo<HighlightInput[]>(
    () =>
      risks.flatMap((r) =>
        (r.evidence ?? []).map((quote) => ({ quote, level: r.level, riskId: r.id })),
      ),
    [risks],
  );
  const segments = useMemo(() => buildHighlightSegments(text, highlights), [text, highlights]);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!activeRiskId || !containerRef.current) return;
    const el = containerRef.current.querySelector(`[data-anchor="${activeRiskId}"]`);
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [activeRiskId]);

  return (
    <div
      ref={containerRef}
      className="whitespace-pre-wrap break-words rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-brand"
    >
      {segments.map((seg, i) =>
        seg.level ? (
          <mark
            key={i}
            data-anchor={seg.anchor ? seg.riskId : undefined}
            className={`rounded px-0.5 ${LEVEL_MARK_CLASS[seg.level]} ${
              activeRiskId === seg.riskId ? 'ring-2 ring-brand-accent ring-offset-1' : ''
            }`}
          >
            {seg.text}
          </mark>
        ) : (
          <span key={i}>{seg.text}</span>
        ),
      )}
    </div>
  );
}
