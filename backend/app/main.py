import logging
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline import validate, InputFile
from app import chat as chat_module, jobs, upstage
from app.schema import ChatRequest, ChatResponse

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="전월세 계약서 리스크 분석 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
    # 업로드 자체의 문제(형식·개수)는 잡을 만들지 않고 즉시 동기 에러로 응답한다.
    err = validate(inputs)
    if err is not None:
        return err.model_dump(exclude_none=True)
    return {"jobId": jobs.start(inputs)}


@app.get("/api/analyze-status/{job_id}")
def analyze_status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="존재하지 않거나 만료된 분석입니다.")
    if job["status"] == "done":
        return {"status": "done", "result": job["result"]}
    return {"status": "running", "step": job["step"]}


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    messages = [m.model_dump() for m in req.messages]
    try:
        reply = chat_module.answer(messages, req.context.model_dump())
    except upstage.RateLimitExceeded:
        reply = "현재 요청이 많아 답변이 지연되고 있습니다. 잠시 후 다시 시도해 주세요."
    return ChatResponse(reply=reply)
