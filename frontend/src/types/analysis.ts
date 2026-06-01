export type RiskLevel = '고위험' | '주의' | '높음' | '보통' | '낮음' | '확인 필요' | '판단 불가';

export type VerificationStatus =
  | '계약서에서 확인됨'
  | '외부 서류 확인 필요'
  | '조건부 해당'
  | '현재 자료만으로 판단 불가';

export type CheckStage = '물건 탐색' | '계약 직전' | '계약서 작성' | '계약 당일' | '잔금 직전' | '입주 직후';

export interface AnalysisSummary {
  type: string;
  parties: string;
  deposit: string;
  duration: string;
  monthlyRent?: string;
  moveInDate?: string;
  balanceDate?: string;
  maintenanceFee?: string;
  realtor?: string;
}

export interface Risk {
  id?: string;
  title?: string;
  level: RiskLevel;
  category?: string;
  clause: string;
  checkSource?: string;
  content: string;
  explanation: string;
  action?: string;
  questions?: string[];
}

export interface RiskAssessment {
  id: string;
  title: string;
  level: RiskLevel;
  status: VerificationStatus;
  category: string;
  requiredDocuments: string[];
  contractClues: string[];
  whyImportant: string;
  currentFinding: string;
  action: string;
  questions: string[];
  stages: CheckStage[];
  dataSource?: string;
}

export interface PublicDocumentCheck {
  name: string;
  checks: string[];
  relatedRisks: string[];
  importance: '높음' | '보통' | '낮음';
  reason: string;
}

export interface StageChecklist {
  stage: CheckStage;
  items: string[];
}

export interface QuestionsByTarget {
  landlord: string[];
  realtor: string[];
  expert: string[];
}

export interface AnalysisData {
  summary: AnalysisSummary;
  riskCounts?: {
    high: number;
    medium: number;
    low: number;
    needCheck: number;
    unknown: number;
  };
  riskAssessments?: RiskAssessment[];
  publicDocumentChecks?: PublicDocumentCheck[];
  stageChecklists?: StageChecklist[];
  questionsByTarget?: QuestionsByTarget;
  finalComment?: string;
  risks: Risk[];
  checklist: string[];
  questions_to_ask: string[];
  providedDocuments?: string[];
}

export interface AnalysisResponse {
  status: 'success' | 'error';
  data?: AnalysisData;
  error?: { code: string; message: string };
}
