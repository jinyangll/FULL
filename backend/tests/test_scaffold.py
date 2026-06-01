from app.scaffold import (
    RISK_SCAFFOLD, RISK_IDS, PUBLIC_DOCUMENT_CHECKS,
    STAGE_CHECKLISTS, QUESTIONS_BY_TARGET, CHECKLIST, QUESTIONS_TO_ASK,
)

EXPECTED_IDS = [
    "jeonse-price-ratio", "trust-registration", "multi-family-collateral",
    "building-legality", "landlord-tax-arrears", "landlord-identity",
    "post-balance-right-change", "multi-home-landlord", "special-clause-risk",
]


def test_nine_categories_present_and_ordered():
    assert RISK_IDS == EXPECTED_IDS
    assert len(RISK_SCAFFOLD) == 9


def test_each_scaffold_has_fixed_fields():
    for item in RISK_SCAFFOLD:
        for key in ("id", "title", "category", "requiredDocuments",
                    "contractClues", "whyImportant", "stages", "questions"):
            assert key in item, f"{item.get('id')} missing {key}"
        assert isinstance(item["stages"], list) and item["stages"]


def test_public_and_stage_constants_nonempty():
    assert len(PUBLIC_DOCUMENT_CHECKS) >= 1
    assert len(STAGE_CHECKLISTS) == 6
    assert set(QUESTIONS_BY_TARGET.keys()) == {"landlord", "realtor", "expert"}
    assert CHECKLIST and QUESTIONS_TO_ASK


def test_every_risk_has_detection_rule():
    from app.scaffold import RISK_IDS, DETECTION_RULES
    for rid in RISK_IDS:
        assert rid in DETECTION_RULES
        assert DETECTION_RULES[rid].strip()


def test_doc_types_includes_contract_and_etc():
    from app.scaffold import DOC_TYPES
    assert "임대차계약서" in DOC_TYPES
    assert "기타" in DOC_TYPES
    assert "등기부등본" in DOC_TYPES
