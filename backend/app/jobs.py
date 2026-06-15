"""비동기 분석 잡 저장소(인메모리, 단일 프로세스 가정).

분석은 3~7분까지 걸릴 수 있어 동기 HTTP 로 붙들지 않고,
잡을 시작한 뒤 진행 단계(step)를 폴링으로 조회한다.
계약서는 민감 정보이므로 결과는 첫 조회 시 전달 즉시 파기하고,
조회되지 않은 잡도 1시간 뒤 가비지컬렉션한다.
"""
import threading
import time
import uuid

from app.pipeline import analyze, InputFile

_TTL_SECONDS = 3600

_jobs: dict[str, dict] = {}
_lock = threading.Lock()


def _gc() -> None:
    now = time.time()
    for k in [k for k, v in _jobs.items() if now - v["created"] > _TTL_SECONDS]:
        del _jobs[k]


def start(inputs: list[InputFile]) -> str:
    """분석을 백그라운드 스레드로 시작하고 job id 를 반환한다."""
    job_id = uuid.uuid4().hex
    with _lock:
        _gc()
        _jobs[job_id] = {"status": "running", "step": 0, "result": None, "created": time.time()}

    def _on_progress(step: int) -> None:
        with _lock:
            if job_id in _jobs:
                _jobs[job_id]["step"] = step

    def _run() -> None:
        resp = analyze(inputs, on_progress=_on_progress)  # analyze 는 내부에서 예외를 흡수한다
        with _lock:
            if job_id in _jobs:
                _jobs[job_id]["status"] = "done"
                _jobs[job_id]["result"] = resp.model_dump(exclude_none=True)

    threading.Thread(target=_run, daemon=True).start()
    return job_id


def get(job_id: str) -> dict | None:
    """잡 상태를 반환한다. 완료된 잡은 결과 전달 즉시 파기한다(서버 무저장 원칙)."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        if job["status"] == "done":
            del _jobs[job_id]
        return dict(job)
