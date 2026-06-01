import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeContract } from '../services/analyzeContract';
import { clearAnalysis, saveAnalysis, savePendingFilesMeta } from '../lib/storage';

type AnalyzeStatus = 'idle' | 'uploading' | 'analyzing' | 'done' | 'error';

export function useAnalyzeContract() {
  const [status, setStatus] = useState<AnalyzeStatus>('idle');
  const navigate = useNavigate();

  const start = useCallback(
    (files: File[]) => {
      clearAnalysis();
      savePendingFilesMeta(files);
      navigate('/analyzing', { state: { files } });
    },
    [navigate],
  );

  const run = useCallback(
    async (files: File[]) => {
      try {
        setStatus('uploading');
        setStatus('analyzing');
        const response = await analyzeContract(files);

        if (response.status === 'success' && response.data) {
          saveAnalysis(response.data);
          setStatus('done');
          return response.data;
        }

        setStatus('error');
        const code = response.error?.code ?? 'analysis_failed';
        navigate(`/error?code=${code}`);
        return null;
      } catch {
        setStatus('error');
        navigate('/error?code=analysis_failed');
        return null;
      }
    },
    [navigate],
  );

  const reset = useCallback(() => {
    setStatus('idle');
    clearAnalysis();
  }, []);

  return { status, start, run, reset };
}
