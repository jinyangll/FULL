import { api } from './api';
import { mockAnalysisResult } from '../mocks/mockAnalysisResult';
import type { AnalysisResponse } from '../types/analysis';

const POLL_INTERVAL_MS = 2000;
const POLL_DEADLINE_MS = 15 * 60 * 1000; // reasoning 분석은 3~7분까지 걸릴 수 있어 여유를 둔다

interface JobStatus {
  status: 'running' | 'done';
  step?: number;
  result?: AnalysisResponse;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export async function analyzeContract(
  files: File[],
  onProgress?: (step: number) => void,
): Promise<AnalysisResponse> {
  if (import.meta.env.VITE_USE_MOCK === 'true') {
    for (let step = 0; step <= 4; step += 1) {
      onProgress?.(step);
      await sleep(700);
    }
    return mockAnalysisResult;
  }

  const form = new FormData();
  files.forEach((file) => form.append('files', file));

  const { data } = await api.post<AnalysisResponse & { jobId?: string }>('/analyze-contract', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  // 업로드 형식·개수 오류는 잡 없이 동기 에러 응답으로 돌아온다.
  if (!data.jobId) {
    return data;
  }

  const deadline = Date.now() + POLL_DEADLINE_MS;
  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL_MS);
    const { data: job } = await api.get<JobStatus>(`/analyze-status/${data.jobId}`);
    if (job.status === 'done' && job.result) {
      return job.result;
    }
    if (typeof job.step === 'number') {
      onProgress?.(job.step);
    }
  }
  throw new Error('분석 시간이 초과되었습니다.');
}
