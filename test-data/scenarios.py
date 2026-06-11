"""테스트 시나리오 정의.

BASELINE = 공통 물건/당사자/기본 계약(안전 계약 기준).
각 시나리오는 BASELINE 위에 contract 일부를 덮어쓰고, 함께 제출할 공적서류(docs)를
명시한다. docs 는 상속하지 않는다(시나리오가 정의한 서류만 PDF 로 생성됨).

실거래가 자동판정 기준(상계주공6, 58.01㎡, 매매중앙값 ≈ 7.36억, 표본 62건):
  - 안전(<80%)  : 보증금 4.5억 → 약 61%
  - 주의(80~90%): 보증금 6.0억 → 약 82%
  - 고위험(≥90%): 보증금 6.8억 → 약 92%
"""
from __future__ import annotations
import copy

DEP_SAFE = 450_000_000
DEP_WARN = 600_000_000
DEP_HIGH = 680_000_000

# 메인 물건: 노원구 상계주공6, 전용 58.01㎡ (국토부 실거래가 매칭 단지)
BASELINE = {
    "property": {
        "addr": "서울특별시 노원구 상계동 666",
        "building": "상계주공6",
        "dong_ho": "601동 1502호",
        "area": "58.01",
        "ptype": "아파트",
    },
    "lessor": {
        "name": "김정환",
        "rrn": "680515-1******",
        "address": "서울특별시 노원구 동일로 1234, 101동 502호",
    },
    "lessee": {
        "name": "박준혁",
        "rrn": "920317-1******",
        "address": "서울특별시 성북구 보문로 55, 302호",
    },
    "contract": {
        "deposit": DEP_SAFE,
        "monthly": 0,
        "term": "2026.07.01. ~ 2028.06.30. (24개월)",
        "balance_date": "2026.07.01.",
        "movein": "2026.07.01.",
        "mgmt_fee": "월 120,000원 (일반관리비, 청소·승강기 포함 / 전기·수도 별도)",
        "special": [
            "임대인은 잔금 지급일 다음 날까지 본 부동산에 근저당권 등 새로운 담보권을 설정하지 아니한다.",
            "임대인은 계약 당시 등기부등본상 권리관계에 변동이 없음을 보증하며, 정보가 사실과 다를 경우 임차인은 계약을 해제할 수 있다.",
            "임차인은 전입신고 및 확정일자를 잔금일 당일 받기로 한다.",
        ],
        "agent": {
            "office": "상계공인중개사사무소", "name": "최영주",
            "regno": "11350-2021-00123", "addr": "서울특별시 노원구 상계로 100",
        },
    },
}

# 안전 케이스 풀세트 공적서류 (정상)
_SAFE_DOCS = {
    "registry": {
        "owner_name": "김정환", "owner_rrn": "680515-1******",
        "owner_address": "서울특별시 노원구 동일로 1234, 101동 502호",
        "trust": False, "mortgages": [],
    },
    "building": {"use": "공동주택(아파트)", "violation": False,
                 "floor": "지상 15층", "approved": "2008-04-25"},
    "residents": [],
    "tax": {"arrears": 0},
    "agent": {"owner": "김정환", "senior": "등기부 을구 근저당권 없음",
              "senior_deposit": "해당 없음", "note": "확인된 특이사항 없음"},
}


SCENARIOS = [
    # ===== A. 데모 3종 =====
    {
        "id": "demo-01-safe", "dir": "demo/01_안전",
        "title": "안전 계약 (전세가율 약 61%)",
        "desc": "전세가율이 안전 범위이고 모든 공적서류가 정상인 깨끗한 계약. 대부분 항목 '낮음'.",
        "triggers": [],
        "contract": {"deposit": DEP_SAFE},
        "docs": copy.deepcopy(_SAFE_DOCS),
    },
    {
        "id": "demo-02-danger", "dir": "demo/02_위험다발",
        "title": "위험 다발 계약 (깡통전세 + 신탁 + 위반 + 체납 + 신원불일치)",
        "desc": "전세가율 92% 깡통전세에 신탁등기·위반건축물·국세체납·임대인 신원불일치·담보권설정금지 특약 부재가 겹친 고위험 계약.",
        "triggers": ["jeonse-price-ratio", "trust-registration", "building-legality",
                     "landlord-tax-arrears", "landlord-identity",
                     "post-balance-right-change", "multi-family-collateral"],
        "contract": {
            "deposit": DEP_HIGH,
            "special": ["임차인은 퇴거 시 도배·장판을 전부 새것으로 교체하여 원상복구한다."],
        },
        "docs": {
            "registry": {
                "owner_name": "이순자", "owner_rrn": "550820-2******",
                "owner_address": "서울특별시 강남구 봉은사로 210",
                "trust": True, "trustee": "㈜한국자산신탁",
                "mortgages": [
                    {"max": 480_000_000, "creditor": "OO저축은행", "joint": True},
                    {"max": 150_000_000, "creditor": "△△캐피탈", "joint": True},
                ],
            },
            "building": {"use": "공동주택(아파트)", "violation": True,
                         "violation_note": "무단 증축(베란다 확장) 및 발코니 구조 변경",
                         "floor": "지상 15층", "approved": "2008-04-25"},
            "residents": [
                {"name": "정O호", "movein": "2019-03-11"},
                {"name": "강O수", "movein": "2021-07-02"},
            ],
            "tax": {"arrears": 52_000_000, "items": [
                {"name": "종합소득세", "amount": 38_000_000, "due": "2025-05-31"},
                {"name": "부가가치세", "amount": 14_000_000, "due": "2025-01-25"},
            ]},
            "trust": {"truster": "이순자", "trustee": "㈜한국자산신탁"},
            "agent": {"owner": "이순자(등기부) / 계약상 임대인 김정환",
                      "senior": "근저당권 2건(채권최고액 합 6.3억) · 신탁등기",
                      "senior_deposit": "선순위 전입세대 2건 확인",
                      "note": "계약상 임대인과 등기부 소유자가 상이함. 신탁등기로 수탁자 동의 필요."},
        },
    },
    {
        "id": "demo-03-edge", "dir": "demo/03_엣지",
        "title": "엣지 케이스 (주의 등급 + 일부 서류 누락)",
        "desc": "전세가율 82% 주의 등급. 집합건물(아파트)이라 다가구 공동담보는 조건부 미해당. 건축물대장·전입세대확인서 미제출로 일부 항목은 '확인 필요'.",
        "triggers": ["jeonse-price-ratio"],
        "contract": {"deposit": DEP_WARN},
        "docs": {
            "registry": {
                "owner_name": "김정환", "owner_rrn": "680515-1******",
                "owner_address": "서울특별시 노원구 동일로 1234, 101동 502호",
                "trust": False,
                "mortgages": [{"max": 120_000_000, "creditor": "OO은행", "joint": False}],
            },
            "agent": {"owner": "김정환", "senior": "근저당권 1건(채권최고액 1.2억)",
                      "senior_deposit": "해당 없음",
                      "note": "건축물대장·전입세대확인서는 계약 전 추가 확인 권고"},
        },
    },

    # ===== B. 위험 9종 (개별 격리) =====
    {
        "id": "risk-01-jeonse", "dir": "risk/01_전세가율과다",
        "title": "전세가율 과다 (깡통전세)",
        "desc": "보증금 6.8억(시세 대비 92%). 계약서만 제출 → 실거래가 자동조회로 전세가율 '고위험' 판정.",
        "triggers": ["jeonse-price-ratio"],
        "contract": {"deposit": DEP_HIGH},
        "docs": {},
    },
    {
        "id": "risk-02-trust", "dir": "risk/02_신탁등기",
        "title": "신탁등기 권리관계",
        "desc": "등기부 갑구에 신탁등기(수탁자 ㈜한국자산신탁) + 신탁원부 제출. 임대 권한이 수탁자에게 있어 동의 확인 필요.",
        "triggers": ["trust-registration"],
        "contract": {"deposit": DEP_SAFE},
        "docs": {
            "registry": {
                "owner_name": "김정환", "owner_rrn": "680515-1******",
                "owner_address": "서울특별시 노원구 동일로 1234, 101동 502호",
                "trust": True, "trustee": "㈜한국자산신탁", "mortgages": [],
            },
            "trust": {"truster": "김정환", "trustee": "㈜한국자산신탁"},
        },
    },
    {
        "id": "risk-03-multifamily", "dir": "risk/03_다가구공동담보",
        "title": "다가구 공동담보 · 선순위 보증금",
        "desc": "단독·다가구주택. 등기부 을구 공동담보 근저당 + 전입세대확인서상 다수 선순위 세대.",
        "triggers": ["multi-family-collateral"],
        "property": {
            "addr": "서울특별시 강서구 화곡동 123-45", "building": "(다가구주택)",
            "dong_ho": "3층 301호", "area": "29.75", "ptype": "단독다가구",
        },
        "contract": {"deposit": 180_000_000},
        "docs": {
            "registry": {
                "owner_name": "김정환", "owner_rrn": "680515-1******",
                "owner_address": "서울특별시 강서구 화곡로 200",
                "trust": False,
                "mortgages": [
                    {"max": 520_000_000, "creditor": "OO은행", "joint": True},
                ],
            },
            "residents": [
                {"name": "한O민", "movein": "2018-02-15", "note": "선순위 전입(101호)"},
                {"name": "오O지", "movein": "2019-08-20", "note": "선순위 전입(201호)"},
                {"name": "신O우", "movein": "2020-11-03", "note": "선순위 전입(202호)"},
                {"name": "배O경", "movein": "2021-05-12", "note": "선순위 전입(302호)"},
            ],
        },
    },
    {
        "id": "risk-04-building", "dir": "risk/04_건축물적법성",
        "title": "건축물 적법성 (위반건축물)",
        "desc": "건축물대장에 위반건축물(무단 증축) 표시. 보증보험 가입 제한 가능.",
        "triggers": ["building-legality"],
        "contract": {"deposit": DEP_SAFE},
        "docs": {
            "building": {"use": "공동주택(아파트)", "violation": True,
                         "violation_note": "무단 증축(베란다 확장, 약 12㎡) 및 대피공간 구조 변경",
                         "floor": "지상 15층", "approved": "2008-04-25"},
        },
    },
    {
        "id": "risk-05-tax", "dir": "risk/05_임대인체납",
        "title": "임대인 국세 체납",
        "desc": "미납국세 열람내역상 임대인 체납 5,200만원. 당해세 우선변제로 보증금 회수 위험.",
        "triggers": ["landlord-tax-arrears"],
        "contract": {"deposit": DEP_SAFE},
        "docs": {
            "tax": {"arrears": 52_000_000, "items": [
                {"name": "종합소득세", "amount": 38_000_000, "due": "2025-05-31"},
                {"name": "부가가치세", "amount": 14_000_000, "due": "2025-01-25"},
            ]},
        },
    },
    {
        "id": "risk-06-identity", "dir": "risk/06_임대인신원불일치",
        "title": "임대인 신원 불일치",
        "desc": "계약상 임대인(김정환)과 등기부 소유자(이순자)가 다름. 권한 없는 자와의 계약 위험.",
        "triggers": ["landlord-identity"],
        "contract": {"deposit": DEP_SAFE},
        "docs": {
            "registry": {
                "owner_name": "이순자", "owner_rrn": "550820-2******",
                "owner_address": "서울특별시 강남구 봉은사로 210",
                "trust": False, "mortgages": [],
            },
        },
    },
    {
        "id": "risk-07-postbalance", "dir": "risk/07_잔금후권리변동",
        "title": "잔금 후 권리 변동 (보호특약 부재)",
        "desc": "담보권설정금지 특약이 없고 잔금일도 미기재. 잔금 전후 근저당 설정을 막을 장치 부재.",
        "triggers": ["post-balance-right-change"],
        "contract": {
            "deposit": DEP_SAFE,
            "balance_date": "",
            "special": ["임차인은 입주 후 시설물을 선량한 관리자의 주의로 사용한다."],
        },
        "docs": {},
    },
    {
        "id": "risk-08-multihome", "dir": "risk/08_악성임대인",
        "title": "악성임대인 명단 일치 (다주택 임대인)",
        "desc": "등기부 소유자(홍길동, 1985년생)가 HUG 상습채무불이행자 명단과 인적사항 일치. ※ USE_FAKE_BLACKLIST=true 로 분석해야 자동 대조가 동작.",
        "triggers": ["multi-home-landlord"],
        "env": {"USE_FAKE_BLACKLIST": "true"},
        "lessor": {"name": "홍길동", "rrn": "850101-1******",
                   "address": "서울특별시 강남구 테헤란로 152"},
        "contract": {"deposit": DEP_SAFE},
        "docs": {
            "registry": {
                "owner_name": "홍길동", "owner_rrn": "850101-1******",
                "owner_address": "서울특별시 강남구 테헤란로 152",
                "trust": False, "mortgages": [],
            },
        },
    },
    {
        "id": "risk-09-special", "dir": "risk/09_특약독소조항",
        "title": "특약 독소조항",
        "desc": "원상복구 과다 전가, 보증금 반환 지연 허용, 수선의무 임차인 전가 등 임차인에게 일방적으로 불리한 특약.",
        "triggers": ["special-clause-risk"],
        "contract": {
            "deposit": DEP_SAFE,
            "special": [
                "임차인은 퇴거 시 도배·장판·싱크대·붙박이장을 전부 새것으로 교체하여 원상복구한다.",
                "보일러·배관 등 주요 설비의 수선비는 전액 임차인이 부담한다.",
                "임대인은 보증금을 임차인 퇴거일로부터 3개월 이내에 반환하며, 지연이자는 지급하지 아니한다.",
                "임차인이 계약기간 중 중도 해지할 경우 보증금의 10%를 위약금으로 임대인에게 귀속시킨다.",
            ],
        },
        "docs": {},
    },
]
