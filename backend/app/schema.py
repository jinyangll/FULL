from typing import Literal, Optional
from pydantic import BaseModel

RiskLevel = Literal["고위험", "주의", "높음", "보통", "낮음", "확인 필요"]
VerificationStatus = Literal[
    "계약서에서 확인됨", "외부 서류 확인 필요", "조건부 해당"
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
    address: Optional[str] = None
    buildingName: Optional[str] = None
    exclusiveArea: Optional[str] = None
    propertyType: Optional[str] = None


class RiskCounts(BaseModel):
    high: int
    medium: int
    low: int
    needCheck: int


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
    evidence: list[str] = []  # 판단 근거가 된 계약서·공적서류 원문 인용
    dataSource: Optional[str] = None  # 공공데이터로 검증된 항목만 출처 표기(예: "국토교통부 실거래가 N건 기준")


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


class SourceDocument(BaseModel):
    docType: str  # "임대차계약서", "등기부등본" 등
    text: str     # 파싱된 원문(프론트 하이라이팅용)


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
    providedDocuments: list[str] = []
    contractText: Optional[str] = None  # 파싱된 계약서 원문(프론트 하이라이팅용·레거시)
    sourceDocuments: list[SourceDocument] = []  # 계약서+공적서류 원문(문서별 하이라이팅용)


class ErrorInfo(BaseModel):
    code: str
    message: str


class AnalysisResponse(BaseModel):
    status: Literal["success", "error"]
    data: Optional[AnalysisData] = None
    error: Optional[ErrorInfo] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: AnalysisData


class ChatResponse(BaseModel):
    reply: str
