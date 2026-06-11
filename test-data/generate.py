"""테스트 데이터 생성기.

scenarios.BASELINE + 각 시나리오를 병합해 계약서·공적서류 HTML 을 만들고,
libreoffice(headless)로 PDF 로 변환한다. 시나리오별 디렉토리에 PDF + 안내(README)를
배치하고, 최상위에 위험↔케이스 매핑표(README.md)를 생성한다.

사용법:
    /home/kangsinu/FULL/backend/.venv/bin/python /home/kangsinu/FULL/test-data/generate.py
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import templates  # noqa: E402
import scenarios  # noqa: E402

OUT = Path(__file__).parent / "out"
_LO_PROFILE = "file:///tmp/lo_profile_testdata"

# 위험 id → 한글 라벨 (매핑표 헤더용)
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


def merge(base: dict, sc: dict) -> dict:
    """BASELINE 위에 시나리오를 얕게 병합한다(키 단위 덮어쓰기). docs 는 상속하지 않는다."""
    m = {
        "property": {**base["property"], **sc.get("property", {})},
        "lessor": {**base["lessor"], **sc.get("lessor", {})},
        "lessee": {**base["lessee"], **sc.get("lessee", {})},
        "contract": {**base["contract"], **sc.get("contract", {})},
        "docs": sc.get("docs", {}),
    }
    for k in ("id", "dir", "title", "desc", "triggers", "env"):
        m[k] = sc.get(k)
    return m


def build_html(m: dict) -> dict[str, str]:
    """문서명(확장자 제외) → HTML. 계약서는 항상, 공적서류는 docs 에 있는 것만."""
    files = {"01_임대차계약서": templates.contract(m)}
    for key, (prefix, fn) in templates.RENDERERS.items():
        if key in m["docs"]:
            files[prefix] = fn(m)
    return files


def convert_dir(html_dir: Path, out_dir: Path) -> None:
    """html_dir 의 모든 .html 을 PDF 로 변환해 out_dir 에 둔다."""
    htmls = sorted(html_dir.glob("*.html"))
    if not htmls:
        return
    subprocess.run(
        ["libreoffice", f"-env:UserInstallation={_LO_PROFILE}",
         "--headless", "--convert-to", "pdf", "--outdir", str(out_dir),
         *(str(h) for h in htmls)],
        check=True, capture_output=True, timeout=180,
    )


def write_manifest(d: Path, m: dict) -> None:
    """시나리오 디렉토리에 안내 파일을 쓴다(업로드 시 참고용)."""
    triggers = "\n".join(f"  - {RISK_LABELS.get(t, t)} ({t})" for t in m["triggers"]) or "  - (없음 / 대부분 낮음)"
    docs = ["01_임대차계약서"] + [templates.RENDERERS[k][0] for k in templates.RENDERERS if k in m["docs"]]
    env = m.get("env") or {}
    env_line = ", ".join(f"{k}={v}" for k, v in env.items()) if env else "(추가 환경변수 없음)"
    lines = [
        f"# {m['title']}", "",
        m["desc"], "",
        "## 포함 문서",
        *(f"- {x}.pdf" for x in docs), "",
        "## 트리거 예상 위험 항목",
        triggers, "",
        "## 분석 시 환경변수",
        env_line, "",
        f"보증금: {m['contract']['deposit']:,}원",
    ]
    (d / "README.txt").write_text("\n".join(lines), encoding="utf-8")


def write_readme(merged_all: list[dict]) -> None:
    """최상위 위험↔케이스 매핑표 + 사용법."""
    risk_ids = list(RISK_LABELS)
    header = "| 시나리오 | " + " | ".join(RISK_LABELS[r] for r in risk_ids) + " |"
    sep = "|" + "---|" * (len(risk_ids) + 1)
    rows = []
    for m in merged_all:
        marks = " | ".join("✅" if r in m["triggers"] else "" for r in risk_ids)
        rows.append(f"| {m['dir']} | {marks} |")
    table = "\n".join([header, sep, *rows])

    text = f"""# 전월세 계약서 분석 — 테스트 데이터

분석 파이프라인(OCR→요약추출→LLM 위험분석 + 실거래가/악성임대인 자동판정)을
검증하기 위한 모의 계약서·공적서류 PDF 모음입니다. **모두 가공된 테스트 문서이며 실제 인물·계약과 무관합니다.**

## 구성

- `out/demo/` — 발표 시연용 3종 (안전 / 위험다발 / 엣지)
- `out/risk/` — 위험 9종을 개별 격리해 트리거하는 세트

각 폴더의 `README.txt` 에 포함 문서·예상 트리거·필요 환경변수가 적혀 있습니다.

## 메인 물건 (실거래가 자동판정 대상)

- 단지: **상계주공6** (서울 노원구 상계동), 전용 **58.01㎡**, 아파트
- 국토부 실거래 매매중앙값 ≈ **7.36억** (표본 62건 기준, 조회 시점에 따라 변동)
- 전세가율 등급: 보증금 4.5억→약 61%(안전) / 6.0억→약 82%(주의) / 6.8억→약 92%(고위험)

> 실거래가는 매월 갱신되므로, 시간이 지나 등급 경계가 흔들리면 `scenarios.py` 의
> `DEP_SAFE/DEP_WARN/DEP_HIGH` 만 조정해 재생성하세요.

## 위험 ↔ 케이스 매핑

{table}

## 분석 시 주의 (자동판정 환경변수)

- **전세가율**: 국토부 실거래가 실조회. `backend/.env` 의 `DATA_GO_KR_KEY` 필요(USE_FAKE_REALPRICE 미설정).
- **악성임대인**(`risk/08_악성임대인`): 실제 HUG 명단은 개인정보라 가짜 명단으로 검증합니다.
  분석 실행 시 **`USE_FAKE_BLACKLIST=true`** 를 설정해야 등기부 소유자(홍길동)가 명단과 대조됩니다.

## 재생성

```bash
/home/kangsinu/FULL/backend/.venv/bin/python /home/kangsinu/FULL/test-data/generate.py
```
"""
    (Path(__file__).parent / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    merged_all = []
    for sc in scenarios.SCENARIOS:
        m = merge(scenarios.BASELINE, sc)
        merged_all.append(m)
        d = OUT / sc["dir"]
        src = d / ".src"
        src.mkdir(parents=True, exist_ok=True)
        for name, html in build_html(m).items():
            (src / f"{name}.html").write_text(html, encoding="utf-8")
        convert_dir(src, d)
        shutil.rmtree(src)
        write_manifest(d, m)
        n_pdf = len(list(d.glob("*.pdf")))
        print(f"  [{sc['dir']}] PDF {n_pdf}개 생성")
    write_readme(merged_all)
    total = len(list(OUT.rglob("*.pdf")))
    print(f"\n완료: 시나리오 {len(scenarios.SCENARIOS)}개, PDF 총 {total}개 → {OUT}")


if __name__ == "__main__":
    main()
