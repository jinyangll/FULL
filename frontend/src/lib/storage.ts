import type { AnalysisData, SourceDocument } from '../types/analysis';

/** 하이라이트용 원본 문서 목록. 구버전 분석(contractText만 있는 경우)도 호환한다. */
export function resolveSourceDocuments(analysis: AnalysisData): SourceDocument[] | undefined {
  if (analysis.sourceDocuments && analysis.sourceDocuments.length > 0) {
    return analysis.sourceDocuments;
  }
  if (analysis.contractText) {
    return [{ docType: '임대차계약서', text: analysis.contractText }];
  }
  return undefined;
}

const ANALYSIS_KEY = 'analysis';
const PENDING_FILE_KEY = 'pending-file-meta';

export interface PendingFileMeta {
  name: string;
  size: number;
  type: string;
}

export function saveAnalysis(data: AnalysisData) {
  sessionStorage.setItem(ANALYSIS_KEY, JSON.stringify(data));
}

export function getAnalysis(): AnalysisData | null {
  const value = sessionStorage.getItem(ANALYSIS_KEY);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as AnalysisData;
  } catch {
    sessionStorage.removeItem(ANALYSIS_KEY);
    return null;
  }
}

export function clearAnalysis() {
  sessionStorage.removeItem(ANALYSIS_KEY);
}

export function savePendingFilesMeta(files: File[]) {
  const metas: PendingFileMeta[] = files.map((file) => ({
    name: file.name,
    size: file.size,
    type: file.type,
  }));
  sessionStorage.setItem(PENDING_FILE_KEY, JSON.stringify(metas));
}

export function getPendingFilesMeta(): PendingFileMeta[] {
  const value = sessionStorage.getItem(PENDING_FILE_KEY);
  if (!value) {
    return [];
  }

  try {
    return JSON.parse(value) as PendingFileMeta[];
  } catch {
    sessionStorage.removeItem(PENDING_FILE_KEY);
    return [];
  }
}

export function clearPendingFileMeta() {
  sessionStorage.removeItem(PENDING_FILE_KEY);
}
