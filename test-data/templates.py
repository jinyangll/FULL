"""테스트용 계약서·공적서류 HTML 템플릿 (7종).

각 함수는 병합된 시나리오 dict(`s`)를 받아 한 문서의 HTML 문자열을 반환한다.
실제 서식을 모방하되, 분석 파이프라인(OCR→extract→LLM)이 핵심 단서를
읽어낼 수 있을 정도의 명확한 텍스트·표 구조를 우선한다.
"""
from __future__ import annotations

_CSS = """
@page { size: A4; margin: 14mm; }
* { box-sizing: border-box; }
body { font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif;
       font-size:10.5pt; color:#000; line-height:1.5; }
h1 { font-size:17pt; text-align:center; margin:0 0 3mm; letter-spacing:2px; }
h2 { font-size:11.5pt; margin:5mm 0 1.5mm; border-bottom:2px solid #000; padding-bottom:1mm; }
p { margin:1.5mm 0; }
table { border-collapse:collapse; width:100%; margin:2mm 0; }
th,td { border:1px solid #333; padding:3px 6px; vertical-align:top; }
th { background:#ececec; font-weight:bold; white-space:nowrap; }
.c{text-align:center} .r{text-align:right} .small{font-size:9pt;color:#222}
.viol{color:#c00;font-weight:bold}
.seal{color:#444}
ol,ul{margin:1mm 0 1mm 6mm;padding:0}
li{margin:1mm 0}
.sub{font-size:9.5pt;color:#333;text-align:center;margin-bottom:3mm}
"""


def _page(title: str, body: str) -> str:
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{_CSS}</style></head>"
        f"<body>{body}</body></html>"
    )


def _won(amount: int) -> str:
    """원 단위 정수 → '6억 8,000만원' 표기."""
    eok = amount // 10**8
    man = (amount % 10**8) // 10**4
    if eok and man:
        return f"{eok}억 {man:,}만원"
    if eok:
        return f"{eok}억원"
    return f"{man:,}만원"


def _full_address(s: dict) -> str:
    p = s["property"]
    return f"{p['addr']} {p['building']} {p['dong_ho']}".strip()


# ---------- 1. 주택임대차계약서 ----------

def contract(s: dict) -> str:
    p, c = s["property"], s["contract"]
    lessor, lessee = s["lessor"], s["lessee"]
    is_jeonse = not c.get("monthly")
    ctype = "전세" if is_jeonse else "월세"
    rows_money = [
        ("보증금", f"금 {_won(c['deposit'])} (₩{c['deposit']:,})"),
        ("계약금", f"금 {_won(c['deposit'] // 10)} (계약 시 지급)"),
    ]
    if c.get("balance_date"):
        rows_money.append(("잔금", f"금 {_won(c['deposit'] - c['deposit']//10)} ({c['balance_date']} 지급)"))
    else:
        rows_money.append(("잔금", "별도 협의 (잔금일 미정)"))
    if c.get("monthly"):
        rows_money.append(("차임(월세)", f"금 {_won(c['monthly'])} (매월 말일 지급)"))
    money_html = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows_money)
    specials = "".join(f"<li>{x}</li>" for x in c.get("special", [])) or "<li>없음</li>"
    movein = c.get("movein", "협의")
    agent = c.get("agent", {})
    body = f"""
    <h1>주택임대차계약서</h1>
    <p class='sub'>[ {ctype} ] · 본 계약서는 주택임대차표준계약서 양식을 따른다.</p>
    <p>임대인(<b>{lessor['name']}</b>)과 임차인(<b>{lessee['name']}</b>)은 아래 표시 부동산에 관하여
    다음 계약 내용과 같이 임대차계약을 체결한다.</p>

    <h2>[부동산의 표시]</h2>
    <table>
      <tr><th>소재지</th><td colspan='3'>{_full_address(s)}</td></tr>
      <tr><th>주택 유형</th><td>{p['ptype']}</td><th>건물 명칭</th><td>{p['building']}</td></tr>
      <tr><th>구조·용도</th><td>철근콘크리트조 / 공동주택({p['ptype']})</td>
          <th>전용면적</th><td>{p['area']}㎡</td></tr>
      <tr><th>임차할 부분</th><td colspan='3'>{p['dong_ho']} 전부</td></tr>
    </table>

    <h2>[계약내용]</h2>
    <table>{money_html}
      <tr><th>관리비</th><td colspan='3'>{c.get('mgmt_fee', '월 100,000원(공용관리비)')}</td></tr>
    </table>

    <h2>[계약기간]</h2>
    <table>
      <tr><th>임대차 기간</th><td>{c['term']}</td></tr>
      <tr><th>입주일(인도일)</th><td>{movein}</td></tr>
    </table>

    <h2>[특약사항]</h2>
    <ol>{specials}</ol>

    <h2>[당사자 인적사항]</h2>
    <table>
      <tr><th></th><th>성명</th><th>주민등록번호</th><th>주소</th></tr>
      <tr><th>임대인</th><td class='c'>{lessor['name']} <span class='seal'>(인)</span></td>
          <td>{lessor['rrn']}</td><td>{lessor['address']}</td></tr>
      <tr><th>임차인</th><td class='c'>{lessee['name']} <span class='seal'>(인)</span></td>
          <td>{lessee['rrn']}</td><td>{lessee['address']}</td></tr>
    </table>

    <h2>[개업공인중개사]</h2>
    <table>
      <tr><th>사무소 명칭</th><td>{agent.get('office', '상계공인중개사사무소')}</td>
          <th>대표</th><td>{agent.get('name', '최영주')}</td></tr>
      <tr><th>등록번호</th><td>{agent.get('regno', '11350-2021-00123')}</td>
          <th>소재지</th><td>{agent.get('addr', '서울특별시 노원구 상계로 100')}</td></tr>
    </table>
    """
    return _page("주택임대차계약서", body)


# ---------- 2. 등기부등본 ----------

def registry(s: dict) -> str:
    p = s["property"]
    r = s["docs"]["registry"]
    # 표제부
    head = f"""
    <h2>【 표제부 】 (1동의 건물의 표시)</h2>
    <table>
      <tr><th>소재지번·건물명칭</th><td>{p['addr']} {p['building']}</td></tr>
      <tr><th>건물내역</th><td>철근콘크리트조 (공동주택 / {p['ptype']})</td></tr>
    </table>
    <h2>【 표제부 】 (전유부분의 건물의 표시)</h2>
    <table>
      <tr><th>건물번호</th><td>{p['dong_ho']}</td><th>전유면적</th><td>{p['area']}㎡</td></tr>
    </table>
    """
    # 갑구 (소유권)
    if r.get("trust"):
        gap_rows = (
            f"<tr><td class='c'>1</td><td>소유권보존</td><td>2008년 5월 2일</td>"
            f"<td>소유자 {r['owner_name']} {r['owner_rrn']}<br>{r['owner_address']}</td></tr>"
            f"<tr><td class='c'>2</td><td>소유권이전(신탁)</td><td>2023년 9월 1일</td>"
            f"<td><b>수탁자 {r['trustee']}</b> 110111-1234567<br>신탁원부 제2023-456호</td></tr>"
        )
        gap_note = "<p class='small viol'>※ 갑구에 신탁등기가 설정되어 있습니다. 실제 처분·임대 권한은 수탁자에게 있을 수 있습니다.</p>"
    else:
        gap_rows = (
            f"<tr><td class='c'>1</td><td>소유권보존</td><td>2008년 5월 2일</td>"
            f"<td>소유자 {r['owner_name']} {r['owner_rrn']}<br>{r['owner_address']}</td></tr>"
        )
        gap_note = ""
    gap = f"""
    <h2>【 갑구 】 (소유권에 관한 사항)</h2>
    <table>
      <tr><th>순위</th><th>등기목적</th><th>접수</th><th>권리자 및 기타사항</th></tr>
      {gap_rows}
    </table>{gap_note}
    """
    # 을구 (소유권 외)
    mortgages = r.get("mortgages", [])
    if mortgages:
        eul_rows = ""
        for i, m in enumerate(mortgages, 1):
            extra = " · 공동담보" if m.get("joint") else ""
            eul_rows += (
                f"<tr><td class='c'>{i}</td><td>근저당권설정{extra}</td>"
                f"<td>채권최고액 금 {_won(m['max'])}</td>"
                f"<td>근저당권자 {m['creditor']}</td></tr>"
            )
        eul = f"""
        <h2>【 을구 】 (소유권 이외의 권리에 관한 사항)</h2>
        <table>
          <tr><th>순위</th><th>등기목적</th><th>채권최고액</th><th>권리자</th></tr>
          {eul_rows}
        </table>
        """
    else:
        eul = ("<h2>【 을구 】 (소유권 이외의 권리에 관한 사항)</h2>"
               "<p>해당 사항 없음 (근저당권 등 설정 내역 없음)</p>")
    body = ("<h1>등기사항전부증명서 (집합건물)</h1>"
            "<p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 등기부등본입니다.</p>"
            + head + gap + eul)
    return _page("등기부등본", body)


# ---------- 3. 건축물대장 ----------

def building(s: dict) -> str:
    p = s["property"]
    b = s["docs"]["building"]
    violation = b.get("violation")
    title_tag = "<span class='viol'>[위반건축물]</span> " if violation else ""
    viol_block = ""
    if violation:
        viol_block = (
            "<h2>【 위반건축물 표시 】</h2>"
            f"<p class='viol'>위반건축물 - {b.get('violation_note', '무단 증축(베란다 확장 및 구조 변경)')}</p>"
            "<p class='small'>시정명령 대상. 위반사항 해소 전까지 전세보증보험 가입이 제한될 수 있습니다.</p>"
        )
    body = f"""
    <h1>{title_tag}집합건축물대장 (전유부)</h1>
    <p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 건축물대장입니다.</p>
    <h2>【 기본 개요 】</h2>
    <table>
      <tr><th>대지위치</th><td colspan='3'>{p['addr']}</td></tr>
      <tr><th>건물명</th><td>{p['building']}</td><th>호명칭</th><td>{p['dong_ho']}</td></tr>
      <tr><th>전유면적</th><td>{p['area']}㎡</td><th>주용도</th><td>{b.get('use', '공동주택(아파트)')}</td></tr>
      <tr><th>층수</th><td>{b.get('floor', '지상 15층')}</td><th>사용승인일</th><td>{b.get('approved', '2008-04-25')}</td></tr>
    </table>
    {viol_block}
    """
    return _page("건축물대장", body)


# ---------- 4. 전입세대확인서 ----------

def residents(s: dict) -> str:
    p = s["property"]
    rs = s["docs"]["residents"]
    if rs:
        rows = "".join(
            f"<tr><td class='c'>{i}</td><td class='c'>{x['name']}</td>"
            f"<td class='c'>{x['movein']}</td><td>{x.get('note','전입')}</td></tr>"
            for i, x in enumerate(rs, 1)
        )
        note = ("<p class='small viol'>※ 동일 건물에 다수의 선순위 전입세대가 확인됩니다. "
                "다가구주택의 경우 선순위 보증금이 후순위 임차인의 회수 순위에 영향을 줄 수 있습니다.</p>")
    else:
        rows = "<tr><td colspan='4' class='c'>해당 주소에 전입된 세대가 없습니다.</td></tr>"
        note = ""
    body = f"""
    <h1>전입세대확인서 (열람용)</h1>
    <p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 전입세대확인서입니다.</p>
    <table><tr><th>열람 대상 주소</th><td>{p['addr']} {p['building']}</td></tr></table>
    <h2>【 전입세대 열람 내역 】</h2>
    <table>
      <tr><th>연번</th><th>세대주</th><th>전입일자</th><th>비고</th></tr>
      {rows}
    </table>
    {note}
    """
    return _page("전입세대확인서", body)


# ---------- 5. 미납국세 열람내역 ----------

def tax(s: dict) -> str:
    t = s["docs"]["tax"]
    lessor = s["lessor"]
    arrears = t.get("arrears", 0)
    if arrears > 0:
        rows = "".join(
            f"<tr><td>{it['name']}</td><td class='r'>{it['amount']:,}원</td>"
            f"<td class='c'>{it.get('due','-')}</td></tr>"
            for it in t.get("items", [])
        )
        total = f"<tr><th>합계</th><th class='r viol'>{arrears:,}원</th><th></th></tr>"
        note = ("<p class='small viol'>※ 미납 국세가 확인됩니다. 공매 시 당해세는 임차인 보증금보다 "
                "우선 변제될 수 있어 보증금 회수에 영향을 줄 수 있습니다.</p>")
    else:
        rows = "<tr><td colspan='3' class='c'>미납 세액이 없습니다. (체납 없음)</td></tr>"
        total = ""
        note = "<p class='small'>※ 조회 기준일 현재 임대인의 미납 국세는 확인되지 않았습니다.</p>"
    body = f"""
    <h1>미납국세 등 열람내역</h1>
    <p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 미납국세 열람내역입니다.</p>
    <table>
      <tr><th>납세자(임대인)</th><td>{lessor['name']}</td>
          <th>주민등록번호</th><td>{lessor['rrn']}</td></tr>
    </table>
    <h2>【 미납 내역 】</h2>
    <table>
      <tr><th>세목</th><th>미납세액</th><th>납기</th></tr>
      {rows}{total}
    </table>
    {note}
    """
    return _page("미납국세열람내역", body)


# ---------- 6. 신탁원부 ----------

def trust(s: dict) -> str:
    tr = s["docs"]["trust"]
    body = f"""
    <h1>신탁원부</h1>
    <p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 신탁원부입니다.</p>
    <h2>【 신탁 당사자 】</h2>
    <table>
      <tr><th>위탁자(원소유자)</th><td>{tr.get('truster', s['lessor']['name'])}</td></tr>
      <tr><th>수탁자(신탁회사)</th><td><b>{tr.get('trustee', '㈜한국자산신탁')}</b></td></tr>
      <tr><th>수익자</th><td>{tr.get('beneficiary', '위탁자 겸 수익자')}</td></tr>
    </table>
    <h2>【 신탁조항 (주요) 】</h2>
    <ul>
      <li>신탁부동산의 처분·임대 등 관리행위는 <b>수탁자가 행한다.</b></li>
      <li>위탁자가 신탁부동산을 임대하려면 <b>수탁자의 사전 서면 동의를 받아야 한다.</b></li>
      <li>수탁자의 동의 없는 임대차는 신탁회사에 대항할 수 없다.</li>
    </ul>
    <p class='small viol'>※ 임대차 계약 시 수탁자({tr.get('trustee', '㈜한국자산신탁')})의 동의서를 반드시 확인해야 합니다.</p>
    """
    return _page("신탁원부", body)


# ---------- 7. 중개대상물 확인·설명서 ----------

def agent_doc(s: dict) -> str:
    a = s["docs"]["agent"]
    body = f"""
    <h1>중개대상물 확인·설명서 (주거용 건축물)</h1>
    <p class='sub'>※ 본 문서는 분석 테스트용으로 작성된 모의 확인·설명서입니다.</p>
    <h2>【 권리관계 】</h2>
    <table>
      <tr><th>소유권</th><td>{a.get('owner', s['lessor']['name'])}</td></tr>
      <tr><th>선순위 권리</th><td>{a.get('senior', '등기부 을구 근저당권 없음')}</td></tr>
      <tr><th>선순위 보증금</th><td>{a.get('senior_deposit', '해당 없음')}</td></tr>
    </table>
    <h2>【 실제 권리관계 또는 공시되지 않은 물건의 권리 】</h2>
    <p>{a.get('note', '확인된 특이사항 없음')}</p>
    <h2>【 관리비 · 비선호시설 】</h2>
    <table>
      <tr><th>관리비</th><td>{a.get('mgmt', '월 100,000원 (일반관리비, 청소비 포함)')}</td></tr>
      <tr><th>체납 세금 설명</th><td>{a.get('tax', '임대인 미납 국세·지방세 열람 권고')}</td></tr>
    </table>
    """
    return _page("중개대상물확인서", body)


# 문서 종류 → (파일명 접두 번호, 렌더 함수). docs 키 존재 시에만 생성.
RENDERERS = {
    "registry": ("02_등기부등본", registry),
    "building": ("03_건축물대장", building),
    "residents": ("04_전입세대확인서", residents),
    "tax": ("05_미납국세열람내역", tax),
    "trust": ("06_신탁원부", trust),
    "agent": ("07_중개대상물확인서", agent_doc),
}
