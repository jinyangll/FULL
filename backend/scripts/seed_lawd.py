"""법정동코드 CSV를 RDS에 적재한다 (최초 1회 또는 갱신 시 실행).

사용법:
    python backend/scripts/seed_lawd.py
"""
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import db  # noqa: E402

_CSV_PATH = Path(__file__).parent.parent / "app" / "data" / "lawd_codes.csv"


def load_csv() -> list[dict]:
    rows = []
    with open(_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({"code5": row["code5"], "sido": row["sido"], "sigungu": row["sigungu"]})
    return rows


def seed(rows: list[dict]) -> None:
    with db.connection() as conn:
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE lawd_codes")
        cur.executemany(
            "INSERT INTO lawd_codes (code5, sido, sigungu) VALUES (%(code5)s, %(sido)s, %(sigungu)s)",
            rows,
        )
    print(f"적재 완료: {len(rows)}건")


def main() -> None:
    rows = load_csv()
    seed(rows)


if __name__ == "__main__":
    main()
