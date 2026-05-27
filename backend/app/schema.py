from typing import Literal, Optional
from pydantic import BaseModel

RiskLevel = Literal["고위험", "주의", "높음", "보통", "낮음", "확인 필요", "판단 불가"]
VerificationStatus = Literal[
    "계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당", "현재 자료만으로 판단 불가"
]
CheckStage = Literal["물건 탐색", "계약 직전", "계약서 작성", "계약 당일", "잔금 직전", "입주 직후"]


class AnalysisSummary(BaseModel):
    type: str
    parties: str
    deposit: str
    duration: str
    monthlyRent: Optional[str] = None
    moveInDate: Optional[str] = None
    balanceDate: Optional[str] = None
    maintenanceFee: Optional[str] = None
    realtor: Optional[str] = None


class RiskCounts(BaseModel):
    high: int
    medium: int
    low: int
    needCheck: int
    unknown: int


class RiskAssessment(BaseModel):
    id: str
    title: str
    level: RiskLevel
    status: VerificationStatus
    category: str
    requiredDocuments: list[str]
    contractClues: list[str]
    whyImportant: str
    currentFinding: str
    action: str
    questions: list[str]
    stages: list[CheckStage]


class PublicDocumentCheck(BaseModel):
    name: str
    checks: list[str]
    relatedRisks: list[str]
    importance: Literal["높음", "보통", "낮음"]
    reason: str


class StageChecklist(BaseModel):
    stage: CheckStage
    items: list[str]


class QuestionsByTarget(BaseModel):
    landlord: list[str]
    realtor: list[str]
    expert: list[str]


class Risk(BaseModel):
    level: RiskLevel
    clause: str
    content: str
    explanation: str


class AnalysisData(BaseModel):
    summary: AnalysisSummary
    riskCounts: RiskCounts
    riskAssessments: list[RiskAssessment]
    publicDocumentChecks: list[PublicDocumentCheck]
    stageChecklists: list[StageChecklist]
    questionsByTarget: QuestionsByTarget
    finalComment: str
    risks: list[Risk]
    checklist: list[str]
    questions_to_ask: list[str]


class ErrorInfo(BaseModel):
    code: str
    message: str


class AnalysisResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[AnalysisData] = None
    error: Optional[ErrorInfo] = None
