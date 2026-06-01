import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import Card from '../components/common/Card';
import LoadingSteps from '../components/loading/LoadingSteps';
import { useAnalyzeContract } from '../hooks/useAnalyzeContract';
import { clearPendingFileMeta, getPendingFilesMeta } from '../lib/storage';

interface LocationState {
  files?: File[];
}

export default function LoadingPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { run } = useAnalyzeContract();
  const [currentStep, setCurrentStep] = useState(0);
  const [apiDone, setApiDone] = useState(false);

  const files = useMemo(() => {
    const state = location.state as LocationState | null;
    if (state?.files && state.files.length > 0) {
      return state.files;
    }

    const metas = getPendingFilesMeta();
    return metas.map((meta) => new File([''], meta.name, { type: meta.type }));
  }, [location.state]);

  useEffect(() => {
    if (files.length === 0) {
      navigate('/', { replace: true });
      return;
    }

    let isMounted = true;
    run(files).then((result) => {
      if (isMounted && result) {
        setApiDone(true);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [files, navigate, run]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setCurrentStep((step) => Math.min(step + 1, 4));
    }, 1500);

    return () => {
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!apiDone) {
      return;
    }

    if (currentStep < 4) {
      setCurrentStep(4);
      return;
    }

    const timer = window.setTimeout(() => {
      clearPendingFileMeta();
      navigate('/report', { replace: true });
    }, 600);

    return () => {
      window.clearTimeout(timer);
    };
  }, [apiDone, currentStep, navigate]);

  const currentMessages = [
    '계약서 파일이 분석 가능한 형식인지 확인하고 있어요.',
    '전월세 계약서의 문장을 읽고 조항 단위로 정리하고 있어요.',
    '보증금, 계약 기간, 임대인·임차인 정보를 리포트에 맞게 구조화하고 있어요.',
    '전세가율, 권리관계, 체납, 특약 등 9가지 전월세 리스크를 점검하고 있어요.',
    '계약 전 확인할 항목을 체크리스트형 리포트로 생성하고 있어요.',
  ];

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-5 py-10 sm:px-6">
      <Card className="w-full max-w-3xl space-y-8 border-slate-200/90 bg-white/95 shadow-[0_28px_80px_rgba(15,23,42,0.12)]">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold text-brand-muted">
              <FileText size={14} aria-hidden="true" />
              <span className="max-w-64 truncate">
                {files.length === 1 ? files[0]?.name : `${files.length}개 파일`}
              </span>
            </div>
            <h1 className="break-keep text-3xl font-bold tracking-normal text-brand">계약서를 분석하고 있어요</h1>
            <p className="break-keep text-sm leading-6 text-brand-muted">1분 정도 걸려요. 잠시만 기다려 주세요.</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-brand">
            {currentStep + 1} / 5 단계
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold text-brand-accent">현재 작업</p>
          <p className="mt-2 break-keep text-sm font-semibold leading-6 text-brand">{currentMessages[currentStep]}</p>
        </div>

        <LoadingSteps currentStep={currentStep} />

        <div className="flex justify-end">
          <button
            type="button"
            className="text-sm font-semibold text-brand-muted hover:text-brand"
            onClick={() => {
              const shouldCancel = window.confirm('분석을 취소할까요? 지금까지의 작업은 저장되지 않아요.');
              if (shouldCancel) {
                clearPendingFileMeta();
                navigate('/');
              }
            }}
          >
            취소
          </button>
        </div>
      </Card>
    </main>
  );
}
