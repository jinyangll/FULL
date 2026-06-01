import { Check, Circle } from 'lucide-react';
import Spinner from '../common/Spinner';

const steps = [
  {
    title: '업로드 문서 유형을 확인하고 있어요',
    description: '계약서와 함께 올린 공적서류의 형식과 용량을 확인해요.',
  },
  {
    title: '계약서의 보증금·기간·특약을 추출하고 있어요',
    description: '보증금, 계약 기간, 관리비, 특약처럼 계약서에서 읽을 수 있는 내용을 정리해요.',
  },
  {
    title: '계약서에서 확인 가능한 항목을 분류하고 있어요',
    description: '계약서만으로 확인할 수 있는 항목과 추가 확인이 필요한 항목을 나눠요.',
  },
  {
    title: '공적서류가 필요한 리스크를 정리하고 있어요',
    description: '등기부등본, 건축물대장, 세금 열람 등 외부 자료가 필요한 항목을 표시해요.',
  },
  {
    title: '전월세 사전 점검 리포트를 생성하고 있어요',
    description: '위험도, 추가 확인 자료, 질문 리스트, 단계별 체크리스트를 정리해요.',
  },
];

export default function LoadingSteps({ currentStep }: { currentStep: number }) {
  const progress = Math.min(((currentStep + 1) / steps.length) * 100, 100);

  return (
    <div className="space-y-7">
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-bold text-brand-muted">
          <span>진행률</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-slate-100 ring-1 ring-slate-200/70">
          <div className="h-full rounded-full bg-brand transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <ol className="space-y-3">
        {steps.map((step, index) => {
          const isDone = index < currentStep;
          const isCurrent = index === currentStep;

          return (
            <li
              key={step.title}
              className={`flex gap-4 rounded-2xl border p-4 transition ${
                isCurrent ? 'border-slate-300 bg-slate-50 shadow-sm' : 'border-transparent bg-white'
              }`}
            >
              <div
                className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border ${
                  isDone
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                    : isCurrent
                      ? 'border-slate-300 bg-white text-brand'
                      : 'border-slate-200 bg-slate-50 text-slate-400'
                }`}
              >
                {isDone ? <Check size={17} aria-hidden="true" /> : null}
                {isCurrent ? <Spinner className="h-4 w-4" /> : null}
                {!isDone && !isCurrent ? <Circle size={10} fill="currentColor" aria-hidden="true" /> : null}
              </div>
              <div className="min-w-0">
                <p className="break-keep font-bold text-brand">{step.title}</p>
                <p className="mt-1 text-sm text-brand-muted">{step.description}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
