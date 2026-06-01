from app import lawd

_TABLE = [
    ("11110", "서울특별시", "종로구"),
    ("11140", "서울특별시", "중구"),
    ("26110", "부산광역시", "중구"),
    ("41135", "경기도", "성남시 분당구"),
]


def test_code_of_simple():
    assert lawd.code_of("서울특별시 종로구 청운동 1-1", _TABLE) == "11110"


def test_code_of_disambiguates_by_sido():
    assert lawd.code_of("부산광역시 중구 OO동", _TABLE) == "26110"
    assert lawd.code_of("서울특별시 중구 OO동", _TABLE) == "11140"


def test_code_of_longest_sigungu():
    assert lawd.code_of("경기도 성남시 분당구 정자동", _TABLE) == "41135"


def test_code_of_no_match():
    assert lawd.code_of("제주특별자치도 어딘가", _TABLE) is None


def test_code_of_empty():
    assert lawd.code_of("", _TABLE) is None


def test_code_of_loads_real_csv():
    # 실제 생성된 CSV 로 직접 조회
    assert lawd.code_of("서울특별시 종로구 청운동", lawd._load_table()) == "11110"
    assert lawd.code_of("세종특별자치시 어진동", lawd._load_table()) == "36110"
