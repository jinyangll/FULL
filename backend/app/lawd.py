"""주소 문자열 → 법정동코드(시군구 5자리) 매칭."""
from __future__ import annotations
import logging

from app import db

logger = logging.getLogger(__name__)

_TABLE: list[tuple[str, str, str]] | None = None


# aws rds 연결 전 - csv에서 직접 읽기
# import csv
# import os
# _CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "lawd_codes.csv")
#
# def _load_table() -> list[tuple[str, str, str]]:
#     """data/lawd_codes.csv 를 (code5, sido, sigungu) 리스트로 로드. 없으면 빈 리스트."""
#     if not os.path.exists(_CSV_PATH):
#         logger.warning("lawd_codes.csv 없음: %s", _CSV_PATH)
#         return []
#     rows = []
#     with open(_CSV_PATH, encoding="utf-8") as f:
#         reader = csv.reader(f)
#         next(reader, None)  # 헤더 스킵
#         for row in reader:
#             if len(row) >= 3:
#                 rows.append((row[0], row[1], row[2]))
#     return rows


# aws rds 연결 후 - rds에서 읽기
def _load_table() -> list[tuple[str, str, str]]:
    """RDS lawd_codes 테이블에서 (code5, sido, sigungu) 리스트를 로드. 실패 시 빈 리스트."""
    try:
        with db.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT code5, sido, sigungu FROM lawd_codes")
            return [(r["code5"], r["sido"], r["sigungu"]) for r in cur.fetchall()]
    except Exception:
        logger.exception("lawd_codes RDS 로드 실패")
        return []


def code_of(address: str, table: list[tuple[str, str, str]] | None = None) -> str | None:
    """주소에서 시도+시군구를 매칭해 5자리 코드 반환. 실패 시 None.
    여러 시군구가 매칭되면 (sido+sigungu) 길이가 가장 긴 것을 택한다."""
    global _TABLE
    if not address:
        return None
    if table is None:
        if _TABLE is None:
            _TABLE = _load_table()
        table = _TABLE
    addr = address.replace(" ", "")
    best = None
    best_len = -1
    for code5, sido, sigungu in table:
        if sido.replace(" ", "") in addr and sigungu.replace(" ", "") in addr:
            length = len(sido) + len(sigungu)
            if length > best_len:
                best_len = length
                best = code5
    return best
