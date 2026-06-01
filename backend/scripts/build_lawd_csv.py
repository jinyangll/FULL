"""행안부 법정동코드 전체자료 TXT → 시군구 단위 CSV(code5,sido,sigungu).

사용법:
    python backend/scripts/build_lawd_csv.py "법정동코드 전체자료.txt"

원본 형식(탭 구분, EUC-KR, CRLF): 법정동코드<TAB>법정동명<TAB>폐지여부('존재'/'폐지')
법정동명 예: '서울특별시 종로구', '서울특별시 종로구 청운동'.
시군구 단위(코드 6~10자리가 0)만 추려 5자리로 출력한다.
"""
import csv
import os
import sys


def main(src: str, dst: str = "backend/app/data/lawd_codes.csv") -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    seen = set()
    rows = []
    with open(src, encoding="euc-kr") as f:
        for line in f:
            parts = line.rstrip().split("\t")  # CRLF 의 \r 까지 제거
            if len(parts) < 3:
                continue
            code, name, status = parts[0], parts[1], parts[2].strip()
            if status != "존재" or len(code) < 10:
                continue
            # 시군구 단위: 뒤 5자리(읍면동·리)가 모두 0
            if code[5:] != "00000":
                continue          # 읍면동·리 제외
            if code[2:5] == "000":
                continue          # 시도 레벨 제외 (시군구 자리가 0)
            tokens = name.split()
            sido = tokens[0]
            # 세종특별자치시처럼 시군구가 없는 단일 토큰은 sigungu=sido 로 둔다
            sigungu = " ".join(tokens[1:]) if len(tokens) >= 2 else tokens[0]
            code5 = code[:5]
            if code5 in seen:
                continue
            seen.add(code5)
            rows.append((code5, sido, sigungu))
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code5", "sido", "sigungu"])
        w.writerows(rows)
    print(f"{len(rows)} rows -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python build_lawd_csv.py <원본_TXT_경로>")
        sys.exit(1)
    main(sys.argv[1])
