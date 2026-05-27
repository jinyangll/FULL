import { api } from './api';
import { mockAnalysisResult } from '../mocks/mockAnalysisResult';
import type { AnalysisResponse } from '../types/analysis';

export async function analyzeContract(file: File): Promise<AnalysisResponse> {
  if (import.meta.env.VITE_USE_MOCK === 'true') {
    await new Promise((resolve) => {
      window.setTimeout(resolve, 1200);
    });
    return mockAnalysisResult;
  }

  const form = new FormData();
  form.append('file', file);

  const { data } = await api.post<AnalysisResponse>('/analyze-contract', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return data;
}
