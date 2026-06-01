import logging
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline import analyze, InputFile

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
    result = analyze(inputs)
    return result.model_dump(exclude_none=True)
