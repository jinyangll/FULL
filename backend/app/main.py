import logging
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline import analyze, InputFile
from app import chat as chat_module, upstage
from app.schema import ChatRequest, ChatResponse

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="전월세 계약서 리스크 분석 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://main.d2skiw5hvuy83a.amplifyapp.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze-contract")
async def analyze_contract(files: list[UploadFile] = File(...)):
    inputs = []
    for f in files:
        file_bytes = await f.read()
        inputs.append(InputFile(file_bytes, f.filename or "upload", f.content_type or ""))
    result = analyze(inputs)
    return result.model_dump(exclude_none=True)


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    messages = [m.model_dump() for m in req.messages]
    try:
        reply = chat_module.answer(messages, req.context.model_dump())
    except upstage.RateLimitExceeded:
        reply = "현재 요청이 많아 답변이 지연되고 있습니다. 잠시 후 다시 시도해 주세요."
    return ChatResponse(reply=reply)
