"""HUG 상습채무불이행자(악성임대인) 명단을 순회 수집해 로컬 CSV 스냅샷을 만든다.

사용법:
    python backend/scripts/crawl_blacklist.py

KHUG 명단(EUC-KR, ~192페이지, ?cur_page=N)을 순회하며 파싱한다.
파싱 로직은 app.blacklist.parse_blacklist_page 를 재사용한다(분석 런타임과 분리).
개인정보이므로 결과 CSV(app/data/blacklist.csv)는 .gitignore 대상이다.
"""
import csv
import os
import sys
import time
from datetime import date

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import blacklist  # noqa: E402

_BASE = "https://www.khug.or.kr/jeonse/web/s01/s010321.jsp"
_UA = "Mozilla/5.0 (X11; Linux x86_64)"
_DST = os.path.join(os.path.dirname(__file__), "..", "app", "data", "blacklist.csv")


def _fetch(cur_page: int) -> str:
    resp = requests.get(_BASE, params={"cur_page": cur_page},
                        headers={"User-Agent": _UA}, timeout=30)
    resp.raise_for_status()
    resp.encoding = "euc-kr"
    return resp.text


def main() -> None:
    first = _fetch(1)
    pages = blacklist.last_page_num(first)
    collected = date.today().isoformat()
    rows = blacklist.parse_blacklist_page(first)
    print(f"총 {pages} 페이지 수집 시작")
    for p in range(2, pages + 1):
        time.sleep(0.7)  # 사이트 부담 최소화
        rows.extend(blacklist.parse_blacklist_page(_fetch(p)))
        if p % 20 == 0:
            print(f"  {p}/{pages} 페이지 ({len(rows)}건)")
    os.makedirs(os.path.dirname(_DST), exist_ok=True)
    with open(_DST, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "birth_year", "age", "address", "deposit_debt", "base_date", "collected_at"])
        for r in rows:
            w.writerow([r["name"], r["birth_year"], r["age"], r["address"],
                        r["deposit_debt"], r["base_date"], collected])
    print(f"{len(rows)}건 -> {_DST}")


if __name__ == "__main__":
    main()
