"""
Comprehensive Test Suite for Phase 2 & Phase 3 LLM Enhancements (Tasks 4, 5, 6, 7, 8).
Validates multi-provider LLM integrations (OpenAI, Gemini, Claude) alongside 100% deterministic fallback paths.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from fastapi.testclient import TestClient

# SQLite JSONB compilation rule for testing
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

from app.database import Base, get_db
from app.main import app as fastapi_app

# Import relevant models
import app.models.user
import app.models.opportunity
import app.models.policy
import app.models.award
import app.models.recipient
import app.models.contact
from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.policy import PolicyStandard, RegulatoryProceeding
from app.models.award import Award
from app.core.membership import get_current_user

# Import engines under test
from app.ingest.nlp_financial_extractor import (
    extract_funding_nlp,
    extract_funding_with_llm,
    clean_corrupted_text,
    KNOWN_PROGRAM_ENVELOPES
)
from app.engine.document_extractor import (
    extract_from_pdf,
    _run_multimodal_ocr,
    _clean_text,
    extract_document_text
)
from app.engine.news_linker import synthesize_regulatory_commercial_impact
from app.engine.teaming_engine import (
    generate_teaming_stack,
    _synthesize_partner_synergy_with_llm
)
from app.engine.capital_stack_engine import (
    calculate_capital_stack,
    _synthesize_diligence_memo
)

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(
        id=1,
        email="test_analyst@aixenergy.io",
        full_name="Lead Energy Analyst",
        role="admin",
        membership_tier="enterprise",
        is_active=True
    )


fastapi_app.dependency_overrides[get_db] = override_get_db
fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(fastapi_app)


# =============================================================================
# Task 4 Tests: Ingestion Pipeline Financial Envelope & Sub-Track Parser
# =============================================================================

def test_nlp_financial_extractor_regex_pass():
    """Verify regex extraction for standard financial amounts."""
    text1 = "Total funding pool of $15 million with maximum award of $2.5M and 20% cost-share requirement."
    tot, max_a, cs = extract_funding_nlp(text1, use_llm_fallback=False)
    assert tot == 15000000.0
    assert max_a == 2500000.0
    assert cs == 20.0


def test_nlp_financial_extractor_title_cleaning():
    """Verify clean_corrupted_text handles quoted character anomalies."""
    corrupted = "'C'o's't'-'S'h'a'r'e' 'P'r'o'g'r'a'm'"
    cleaned = clean_corrupted_text(corrupted)
    assert "Cost-Share Program" in cleaned or "CostShare Program" in cleaned


def test_nlp_financial_extractor_llm_mocked():
    """Verify extract_funding_with_llm accurately parses complex multi-tier figures when mocked."""
    complex_text = "The Commission authorizes funding across Track 1 ($5M pool) and Track 2 ($10M pool) up to $3M ceiling."
    
    mock_response = {
        "total_funding": 15000000.0,
        "max_per_award": 3000000.0,
        "cost_share_pct": 25.0,
        "concept_paper_required": True,
        "concept_paper_deadline": "2026-11-01",
        "funding_sub_tracks": [
            {"track_name": "Track 1", "allocation": 5000000.0, "max_award": 1500000.0},
            {"track_name": "Track 2", "allocation": 10000000.0, "max_award": 3000000.0}
        ],
        "cost_share_explanation": "25% non-state matching required for private commercial entities."
    }

    with patch("app.ingest.nlp_financial_extractor.extract_funding_with_llm", return_value=mock_response):
        tot, max_a, cs = extract_funding_nlp("Unstructured complex grant text", use_llm_fallback=True)
        assert tot == 15000000.0
        assert max_a == 3000000.0
        assert cs == 25.0


# =============================================================================
# Task 5 Tests: Multimodal OCR & Visual Structure Recovery for Scanned PDFs
# =============================================================================

def test_document_extractor_clean_text():
    """Verify document text cleaning and whitespace normalization."""
    raw = "  Line 1   \n\n\n\n\x00Line 2   \r\n   "
    cleaned = _clean_text(raw)
    assert "Line 1" in cleaned
    assert "Line 2" in cleaned
    assert "\x00" not in cleaned


def test_document_extractor_multimodal_ocr_fallback():
    """Verify _run_multimodal_ocr returns empty string gracefully when no API keys are set."""
    with patch("app.config.settings.openai_api_key", None), \
         patch("app.config.settings.gemini_api_key", None), \
         patch("app.config.settings.anthropic_api_key", None), \
         patch.dict("os.environ", {}, clear=True):
        ocr_out = _run_multimodal_ocr([b"fake_png_bytes"])
        assert ocr_out == ""


def test_document_extractor_multimodal_ocr_mocked():
    """Verify PDF extraction switches doc_type to Scanned PDF when OCR succeeds."""
    mock_ocr_text = "### Project Executive Summary\nThis scanned project proposal details a 100 MW Long-Duration Energy Storage facility with a total budget of $45,000,000."
    
    with patch("app.engine.document_extractor._run_multimodal_ocr", return_value=mock_ocr_text):
        # Create minimal PDF bytes using pymupdf
        import pymupdf as fitz
        doc = fitz.open()
        page = doc.new_page() # blank page -> 0 text
        pdf_bytes = doc.tobytes()
        doc.close()

        res = extract_from_pdf(pdf_bytes, "scanned_proposal.pdf")
        assert res["status"] == "success"
        assert res["doc_type"] == "Scanned PDF (Multimodal OCR Recovered)"
        assert "100 MW Long-Duration Energy Storage" in res["text"]


# =============================================================================
# Task 6 Tests: Regulatory Docket & PSC Proceeding Commercial Impact Synthesizer
# =============================================================================

def test_regulatory_impact_synthesizer_deterministic():
    """Verify deterministic fallback for regulatory commercial impact synthesis."""
    result = synthesize_regulatory_commercial_impact(
        item_type="proceeding",
        identifier="NYPSC Case 18-E-0130",
        title="Energy Storage Deployment and Interconnection Policy",
        summary="Statewide proceeding establishing bulk and retail energy storage procurement mandates.",
        mandate_or_tailwinds="Establishes 6 GW energy storage mandate by 2030 and index storage credits.",
        friction_points="Interconnection study backlog across upstate transmission zones.",
        linked_technologies=["Long-Duration Energy Storage", "Lithium-Ion BESS"]
    )

    assert result["status"] == "success"
    assert "impacted_stakeholders" in result
    assert len(result["impacted_stakeholders"]) >= 3
    assert len(result["bottlenecks_and_risks"]) >= 1
    assert len(result["monetization_pathways"]) >= 2
    assert "Interconnection study backlog" in result["bottlenecks_and_risks"][0]
    assert len(result["executive_synthesis"]) > 50


def test_regulatory_impact_api_endpoints():
    """Verify GET /api/policies/{id}/commercial-impact and GET /api/policies/proceedings/{id}/commercial-impact."""
    # Test Policy Standard endpoint (e.g. NFPA-855 or seed policy)
    resp_pol = client.get("/api/policies/NFPA-855/commercial-impact")
    assert resp_pol.status_code == 200
    pol_data = resp_pol.json()
    assert pol_data["status"] == "success"
    assert "impacted_stakeholders" in pol_data
    assert "executive_synthesis" in pol_data

    # Test Proceeding endpoint (e.g. FERC-ORDER-1920 or NYPSC-STORAGE-PROCEEDING)
    resp_proc = client.get("/api/policies/proceedings/FERC-ORDER-1920/commercial-impact")
    assert resp_proc.status_code == 200
    proc_data = resp_proc.json()
    assert proc_data["status"] == "success"
    assert "impacted_stakeholders" in proc_data
    assert "bottlenecks_and_risks" in proc_data


# =============================================================================
# Task 7 Tests: Teaming Partner Strategic Synergy & Complementary Rationale Generator
# =============================================================================

def test_teaming_partner_synergy_deterministic():
    """Verify deterministic fallback for teaming synergy synthesis."""
    partners = [
        {
            "id": "partner_cornell_university",
            "name": "Cornell University",
            "type": "university",
            "role_title": "Academic Research & Validation Anchor",
            "precedent_award_count": 8,
            "historical_funding_won": 12500000.0,
            "location": "Ithaca, NY"
        },
        {
            "id": "partner_con_edison",
            "name": "Consolidated Edison",
            "type": "utility",
            "role_title": "Utility / Demonstration Host Site",
            "precedent_award_count": 4,
            "historical_funding_won": 8000000.0,
            "location": "New York, NY"
        }
    ]

    synth = _synthesize_partner_synergy_with_llm(
        opportunity_name="PON 6088 High-Efficiency Building Decarbonization",
        agency="NYSERDA",
        target_technology="Building Decarbonization",
        lead_company_name="CleanTech Dynamics Inc",
        partners=partners
    )

    assert "partner_synergies" in synth
    assert "partner_cornell_university" in synth["partner_synergies"]
    assert "Cornell University" in synth["partner_synergies"]["partner_cornell_university"]
    assert "consortia_rationale" in synth
    assert len(synth["consortia_rationale"]) > 50


def test_generate_teaming_stack_integration():
    """Verify generate_teaming_stack attaches strategic_synergy_rationale to each recommended partner."""
    db = TestingSessionLocal()
    try:
        # Seed an opportunity and award if needed
        opp = Opportunity(
            id=1001,
            solicitation_number="PON 6141",
            name="Grid Energy Storage Acceleration Program",
            agency="NYSERDA",
            total_funding=20000000.0,
            max_per_award=4000000.0
        )
        db.add(opp)

        award1 = Award(
            id=5001,
            project_title="Advanced Vanadium Flow Battery Grid Storage",
            recipient_name="Columbia University",
            recipient_type="university",
            recipient_state="NY",
            recipient_city="New York",
            pi_name="Dr. Elena Vance",
            pi_email="evance@columbia.edu",
            award_amount=2500000.0
        )
        db.add(award1)
        db.commit()

        stack = generate_teaming_stack(
            db=db,
            opp_id=1001,
            technology_area="Energy Storage",
            state_scope="NY",
            lead_company_name="Apex Power Storage LLC"
        )

        assert stack["opportunity_id"] == 1001
        assert "recommended_partners" in stack
        assert len(stack["recommended_partners"]) > 0
        for partner in stack["recommended_partners"]:
            assert "strategic_synergy_rationale" in partner
            assert len(partner["strategic_synergy_rationale"]) > 20
        assert "consortia_rationale" in stack
        assert "strategic_synergies_synthesized_by" in stack
    finally:
        db.close()


# =============================================================================
# Task 8 Tests: Fiduciary Capital Stack & Blended WACC Diligence Memorandum
# =============================================================================

def test_capital_stack_diligence_memo_deterministic():
    """Verify investment committee memorandum synthesis."""
    res = calculate_capital_stack(
        project_cost=15_000_000.0,
        matched_grant_max=3_000_000.0,
        technology_category="Energy Storage",
        technology_areas=["Long-Duration Energy Storage", "BESS"],
        project_summary="100 MWh utility-scale iron-air energy storage facility.",
        applicant_type="Commercial Project Sponsor",
        solicitation_name="High-Capacity Energy Storage Facility",
        agency="NYSERDA / DOE",
        energy_community_bonus=True,
        domestic_content_bonus=False,
        prevailing_wage_compliant=True,
        tax_exempt_direct_pay=False
    )

    assert "investment_committee_memo" in res
    assert "memo_synthesized_by" in res
    memo = res["investment_committee_memo"]
    
    assert len(memo.strip()) > 100
    assert "Capital Structure" in memo
    assert "WACC" in memo or "Cost of Capital" in memo
    assert "Statutory" in memo or "Tax" in memo

    # Verify WACC metrics
    assert res["summary"]["blended_wacc_pct"] < res["summary"]["unsubsidized_wacc_pct"]
    assert res["summary"]["wacc_savings_bps"] > 0
    assert res["summary"]["ten_year_cumulative_savings"] > 0


def test_capital_stack_api_endpoint():
    """Verify POST /api/capital-stack endpoint returns complete memo and audit data."""
    payload = {
        "project_cost": 20000000.0,
        "matched_grant_max": 5000000.0,
        "technology_category": "Clean Hydrogen",
        "technology_areas": ["PEM Electrolyzer", "Hydrogen Storage"],
        "project_summary": "20 MW green hydrogen electrolysis hub for industrial decarbonization.",
        "applicant_type": "Commercial Corporation",
        "solicitation_name": "Regional Clean Hydrogen Initiative",
        "agency": "DOE / NYSERDA",
        "energy_community_bonus": True,
        "domestic_content_bonus": True,
        "prevailing_wage_compliant": True,
        "tax_exempt_direct_pay": False
    }

    resp = client.post("/api/capital-stack", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "investment_committee_memo" in data
    assert "memo_synthesized_by" in data
    assert data["is_tax_credit_eligible"] is True
    assert "waterfall_layers" in data
    assert len(data["waterfall_layers"]) == 4
