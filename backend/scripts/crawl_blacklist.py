"""HUG 상습채무불이행자(악성임대인) 명단을 순회 수집해 RDS에 갈아끼운다.

사용법:
    python backend/scripts/crawl_blacklist.py

KHUG 명단(EUC-KR, ~192페이지, ?cur_page=N)을 순회하며 파싱한다.
파싱 로직은 app.blacklist.parse_blacklist_page 를 재사용한다(분석 런타임과 분리).
"""
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# 단독 실행이라 .env를 직접 로드 (main.py를 안 거치므로)
load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import blacklist  # noqa: E402
from app import db         # noqa: E402

_BASE = "https://www.khug.or.kr/jeonse/web/s01/s010321.jsp"
_UA = "Mozilla/5.0 (X11; Linux x86_64)"


def _fetch(cur_page: int) -> str:
    resp = requests.get(
        _BASE,
        params={"cur_page": cur_page},
        headers={"User-Agent": _UA},
        timeout=30,
    )
    resp.raise_for_status()
    resp.encoding = "euc-kr"
    return resp.text


def fetch_all_rows() -> list[dict]:
    """모든 페이지를 순회하며 명단 행을 모은다."""
    first = _fetch(1)
    pages = blacklist.last_page_num(first)
    rows = blacklist.parse_blacklist_page(first)
    print(f"총 {pages} 페이지 수집 시작")
    for p in range(2, pages + 1):
        time.sleep(0.7)  # 사이트 부담 최소화
        rows.extend(blacklist.parse_blacklist_page(_fetch(p)))
        if p % 20 == 0:
            print(f"  {p}/{pages} 페이지 ({len(rows)}건)")
    return rows


def replace_blacklist(rows: list[dict]) -> None:
    """기존 명단을 전부 비우고 새 명단으로 갈아끼운다 (한 트랜잭션)."""
    with db.connection() as conn:
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE blacklist")
        cur.executemany(
            """INSERT INTO blacklist
               (name, age, address, deposit_debt, base_date, birth_year)
               VALUES (%(name)s, %(age)s, %(address)s,
                       %(deposit_debt)s, %(base_date)s, %(birth_year)s)""",
            rows,
        )
    print(f"갈아끼우기 완료: {len(rows)}건")


def main() -> None:
    rows = fetch_all_rows()
    replace_blacklist(rows)


if __name__ == "__main__":
    main()