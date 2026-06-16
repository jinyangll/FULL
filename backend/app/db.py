"""RDS(MySQL) 연결 헬퍼
쿼리는 안 날리고 연결을 열고 닫는 것만 담당
실제 SELECT/INSERT는 blacklist.py(조회)와 crawl_blacklist.py(저장)에서 작성함
"""
from __future__ import annotations
import os
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor


def _config() -> dict:
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ["DB_NAME"],
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
    }


@contextmanager
def connection():
    """with db.connection() as conn: 형태로 사용. 정상 종료 시 커밋, 에러 시 롤백."""
    conn = pymysql.connect(**_config())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()