"""정확도 자동 채점 하네스.

test-data/out/ 의 12개 시나리오 PDF 를 실제 분석 파이프라인(pipeline.analyze)에 넣고,
scenarios.py 의 triggers 라벨(정답지)과 비교해 카테고리별 recall / 오탐을 채점한다.

채점 기준:
- 트리거 라벨 항목  → level 이 "높음" 또는 "주의" 면 적중(hit)
- 비트리거 항목     → level 이 "높음" 이면 오탐(FP), "주의" 면 soft-FP 로 별도 집계
  ("확인 필요"는 서류 미제출 시 정상 동작이므로 오탐으로 보지 않는다)

사용법:
    /home/kangsinu/FULL/backend/.venv/bin/python /home/kangsinu/FULL/test-data/evaluate.py
    옵션: --only risk/01_전세가율과다  (특정 시나리오만)
          --workers 3                  (병렬 분석 수, 기본 3)

산출물: test-data/eval_results.json (원시 결과), test-data/eval_report.md (채점표)

주의: 실제 Upstage/국토부 API 를 호출하므로 시나리오당 3~7분 + 비용이 든다.
USE_FAKE_BLACKLIST=true 를 전체에 적용한다(가짜 명단은 홍길동/1985 만 매칭되므로
risk/08 외 시나리오에는 영향이 없다 — scenarios.py 의 lessor 가 홍길동인 것은 risk-08 뿐).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
BACKEND = HERE.parent / "backend"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND / ".env")
os.environ["USE_FAKE_BLACKLIST"] = "true"

import scenarios  # noqa: E402
from app.pipeline import analyze, InputFile  # noqa: E402
from app.scaffold import RISK_IDS  # noqa: E402

OUT = HERE / "out"
FLAGGED = {"높음", "주의"}

RISK_LABELS = {
    "jeonse-price-ratio": "전세가율",
    "trust-registration": "신탁등기",
    "multi-family-collateral": "다가구담보",
    "building-legality": "건축물적법성",
    "landlord-tax-arrears": "임대인체납",
    "landlord-identity": "임대인신원",
    "post-balance-right-change": "잔금후권리변동",
    "multi-home-landlord": "악성임대인",
    "special-clause-risk": "특약독소",
}


def load_inputs(d: Path) -> list[InputFile]:
    return [
        InputFile(p.read_bytes(), p.name, "application/pdf")
        for p in sorted(d.glob("*.pdf"))
    ]


def run_scenario(sc: dict) -> dict:
    """한 시나리오를 분석하고 카테고리별 level 을 반환한다."""
    d = OUT / sc["dir"]
    t0 = time.time()
    try:
        resp = analyze(load_inputs(d))
    except Exception as exc:  # 분석 자체가 죽으면 채점표에 에러로 남긴다
        return {"dir": sc["dir"], "triggers": sc["triggers"], "error": repr(exc),
                "levels": {}, "seconds": round(time.time() - t0)}
    if resp.status != "success":
        return {"dir": sc["dir"], "triggers": sc["triggers"],
                "error": f"{resp.error.code}: {resp.error.message}",
                "levels": {}, "seconds": round(time.time() - t0)}
    levels = {a.id: a.level for a in resp.data.riskAssessments}
    return {"dir": sc["dir"], "triggers": sc["triggers"], "error": None,
            "levels": levels, "seconds": round(time.time() - t0)}


def score(results: list[dict]) -> dict:
    """카테고리별 hit/miss/FP 집계."""
    per_cat = {rid: {"hits": 0, "misses": 0, "fp": 0, "soft_fp": 0, "miss_at": [], "fp_at": []}
               for rid in RISK_IDS}
    for r in results:
        if r["error"]:
            continue
        for rid in RISK_IDS:
            level = r["levels"].get(rid, "")
            c = per_cat[rid]
            if rid in r["triggers"]:
                if level in FLAGGED:
                    c["hits"] += 1
                else:
                    c["misses"] += 1
                    c["miss_at"].append(f'{r["dir"]}({level})')
            else:
                if level == "높음":
                    c["fp"] += 1
                    c["fp_at"].append(r["dir"])
                elif level == "주의":
                    c["soft_fp"] += 1
    return per_cat


def write_report(results: list[dict], per_cat: dict) -> None:
    ok = [r for r in results if not r["error"]]
    errs = [r for r in results if r["error"]]
    total_hits = sum(c["hits"] for c in per_cat.values())
    total_expected = sum(c["hits"] + c["misses"] for c in per_cat.values())
    total_fp = sum(c["fp"] for c in per_cat.values())
    recall_pct = round(100 * total_hits / total_expected) if total_expected else 0

    lines = [
        "# 정확도 채점 리포트", "",
        f"- 시나리오: {len(ok)}/{len(results)}개 분석 성공"
        + (f" (실패 {len(errs)}건)" if errs else ""),
        f"- **전체 recall: {total_hits}/{total_expected} ({recall_pct}%)**, 오탐(높음): {total_fp}건", "",
        "## 카테고리별", "",
        "| 카테고리 | 적중 | 누락 | 오탐(높음) | 주의 처리 | 누락 위치 |",
        "|---|---|---|---|---|---|",
    ]
    for rid in RISK_IDS:
        c = per_cat[rid]
        n = c["hits"] + c["misses"]
        lines.append(
            f'| {RISK_LABELS[rid]} | {c["hits"]}/{n if n else "-"} | {c["misses"]} '
            f'| {c["fp"]}{"(" + ", ".join(c["fp_at"]) + ")" if c["fp_at"] else ""} '
            f'| {c["soft_fp"]} | {", ".join(c["miss_at"]) or "-"} |'
        )
    lines += ["", "## 시나리오별 결과", "",
              "| 시나리오 | 소요(초) | " + " | ".join(RISK_LABELS[r] for r in RISK_IDS) + " |",
              "|---|---|" + "---|" * len(RISK_IDS)]
    for r in results:
        if r["error"]:
            lines.append(f'| {r["dir"]} | {r["seconds"]} | 분석 실패: {r["error"]} ' + "| " * (len(RISK_IDS) - 1) + "|")
            continue
        cells = []
        for rid in RISK_IDS:
            level = r["levels"].get(rid, "?")
            expected = rid in r["triggers"]
            mark = "✅" if (expected and level in FLAGGED) else ("❌" if expected else "")
            if not expected and level == "높음":
                mark = "⚠️"
            cells.append(f"{mark}{level}")
        lines.append(f'| {r["dir"]} | {r["seconds"]} | ' + " | ".join(cells) + " |")
    lines += ["", "범례: ✅ 트리거 적중 / ❌ 트리거 누락 / ⚠️ 비트리거인데 높음(오탐)", ""]
    (HERE / "eval_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="특정 시나리오 dir 만 (예: risk/01_전세가율과다)")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    targets = [s for s in scenarios.SCENARIOS if not args.only or s["dir"] == args.only]
    if not targets:
        sys.exit(f"시나리오 없음: {args.only}")
    print(f"{len(targets)}개 시나리오 평가 시작 (workers={args.workers})", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(run_scenario, targets))
    for r in results:
        status = r["error"] or "ok"
        print(f'  [{r["dir"]}] {r["seconds"]}s {status}', flush=True)

    (HERE / "eval_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(results, score(results))
    print(f"\n완료 → {HERE / 'eval_report.md'}", flush=True)


if __name__ == "__main__":
    main()
