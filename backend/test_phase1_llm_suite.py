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
# Import all models before create_all
import app.models.user
import app.models.opportunity
import app.models.proposal
import app.models.contact
import app.models.admin_email
import app.models.foa_shred

from app.models.user import User
from app.core.membership import get_current_user
from app.models.opportunity import Opportunity, OpportunityRestriction
from app.models.proposal import Proposal
from app.models.admin_email import ContactEmailThread, ContactEmailMessage
from app.models.contact import Contact
from app.models.foa_shred import FoaShredResult
from app.api.foa_shredder import _synthesize_shred_blueprint, _synthesize_shred_blueprint_with_llm
from app.api.proposals import _generate_agency_sopo_and_rubric, _run_red_team_audit_with_llm
from app.services.conversation_summarizer import summarize_conversation_thread
from app.main import app

# In-memory SQLite with StaticPool so all connections share the same memory instance
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
        email="admin@aixenergy.io",
        full_name="Admin Principal",
        role="admin",
        is_active=True
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

@pytest.fixture(autouse=True)
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================================================================
# COMPONENT 1: DYNAMIC FOA SHREDDER TESTS
# ==============================================================================

def test_foa_shredder_deterministic_fallback(db_session):
    """Test deterministic blueprint synthesis when no LLMs are invoked."""
    opp = Opportunity(
        id=9991,
        name="Advanced Long-Duration Storage FOA",
        solicitation_number="PON-9999",
        agency="NYSERDA",
        total_funding=15000000.0,
        max_per_award=3000000.0,
        cost_share_pct=20.0,
        short_description="Statewide solicitation for 100-hour grid battery pilots."
    )
    db_session.merge(opp)
    db_session.commit()

    restrictions = db_session.query(OpportunityRestriction).filter(OpportunityRestriction.opportunity_id == opp.id).all()
    blueprint = _synthesize_shred_blueprint(opp, restrictions)

    assert "scoring_rubric_json" in blueprint
    assert len(blueprint["scoring_rubric_json"]) >= 3
    assert "submission_checklist_json" in blueprint
    assert len(blueprint["submission_checklist_json"]) >= 3
    assert "key_win_themes" in blueprint
    assert "red_team_fatal_flaws_to_avoid" in blueprint
    assert blueprint["cost_share_required_pct"] >= 0.0

def test_foa_shredder_llm_synthesis(db_session):
    """Test LLM extraction branch for FOA shredder."""
    opp = Opportunity(
        id=9992,
        name="ARPA-E OPEN Energy Paradigm Shift",
        solicitation_number="DE-FOA-0003001",
        agency="ARPA-E",
        total_funding=50000000.0,
        max_per_award=5000000.0,
        cost_share_pct=10.0,
        short_description="Transformational high-risk disruptive energy tech."
    )
    db_session.merge(opp)
    db_session.commit()

    mock_llm_output = {
        "executive_summary": "High-risk, transformative R&D paradigm shift opportunity.",
        "cost_share_required_pct": 10.0,
        "cost_share_rule_explanation": "10% matching required for early-stage university-led teams.",
        "trl_min": 2,
        "trl_max": 5,
        "eligible_applicant_types": ["Universities", "National Labs", "Startups"],
        "domestic_manufacturing_clause": True,
        "justice40_cbp_required": True,
        "scoring_rubric_json": [
            {"criterion": "Technical Innovation & Impact", "weight_pct": 50, "description": "Disruptive potential", "key_focus": "Physics validation"},
            {"criterion": "Team Qualifications & Capabilities", "weight_pct": 30, "description": "Principal investigator track record", "key_focus": "Execution readiness"},
            {"criterion": "Commercialization Strategy", "weight_pct": 20, "description": "Path to T-to-M", "key_focus": "Market adoption"}
        ],
        "submission_checklist_json": [
            {"volume": "Volume 1", "section_title": "Technical Narrative", "page_limit": "20 pages", "required": True, "notes": "Strict font rules"},
            {"volume": "Volume 2", "section_title": "Budget Justification", "page_limit": "Excel SF-424A", "required": True, "notes": "Allowable costs only"}
        ],
        "key_win_themes": ["Clear techno-economic advantage vs lithium-ion", "Strong milestone-gated SOPO"],
        "red_team_fatal_flaws_to_avoid": ["Incremental progress over existing baselines", "Failure to disclose subrecipients"]
    }

    with patch("app.api.foa_shredder.settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.gemini_api_key = ""
        mock_settings.anthropic_api_key = ""
        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_resp = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = json.dumps(mock_llm_output)
            mock_resp.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_resp

            shred = _synthesize_shred_blueprint_with_llm(opp, [])
            assert shred["cost_share_required_pct"] == 10.0
            assert len(shred["scoring_rubric_json"]) == 3
            assert shred["scoring_rubric_json"][0]["criterion"] == "Technical Innovation & Impact"
            assert "Clear techno-economic advantage vs lithium-ion" in shred["key_win_themes"]

def test_foa_shredder_endpoint_and_cache(db_session):
    """Test FOA shredder API endpoint with persistence."""
    opp = Opportunity(
        id=9993,
        name="CEC Clean Heavy Transportation Grant",
        solicitation_number="GFO-26-502",
        agency="California Energy Commission (CEC)",
        total_funding=45000000.0,
        max_per_award=10000000.0,
        cost_share_pct=25.0,
        short_description="Deployment of zero-emission freight trucks and high-power depot chargers."
    )
    db_session.merge(opp)
    db_session.commit()

    resp = client.get(f"/api/foa-shredder/{opp.id}?force_refresh=true")
    assert resp.status_code == 200
    data = resp.json()

    assert data["opportunity_id"] == opp.id
    assert "scoring_rubric" in data
    assert isinstance(data["scoring_rubric"], list)
    assert len(data["scoring_rubric"]) >= 3
    assert "submission_checklist" in data
    assert "key_win_themes" in data
    assert "red_team_fatal_flaws_to_avoid" in data

    # Verify cached entry in SQLite DB
    cached = db_session.query(FoaShredResult).filter_by(opportunity_id=opp.id).first()
    assert cached is not None
    assert cached.solicitation_number == "GFO-26-502"

# ==============================================================================
# COMPONENT 2: DYNAMIC SOPO/WBS & RED-TEAM AUDIT TESTS
# ==============================================================================

def test_proposal_sopo_and_wbs_generation():
    """Test dynamic context-aware SOPO and rubric generator."""
    sopo_tasks, rubric_scores = _generate_agency_sopo_and_rubric(
        agency="U.S. Department of Energy",
        tech_area="Clean Hydrogen",
        award_amount=2000000.0,
        recipient_name="Advanced H2 Corp",
        pi_name="Dr. Jane Doe",
        project_title="Electrolyzer Durability Enhancement",
        project_description="Developing 100kW solid oxide electrolyzer cells operating at high current density with 45V compliance."
    )

    assert len(sopo_tasks) >= 3
    for task in sopo_tasks:
        assert "task" in task
        assert "budget" in task
        assert "milestone" in task
        assert "gate" in task
        assert "trl" in task

    assert len(rubric_scores) >= 3
    for r in rubric_scores:
        assert "criterion" in r
        assert "max_pts" in r
        assert "score" in r
        assert "feedback" in r

def test_proposal_red_team_audit_workflow(db_session):
    """Test proposal red-team audit endpoint with rubric recalculation."""
    test_prop = Proposal(
        id="prop-test-red-team-001",
        solicitation_number="PON-5482",
        title="10 MW Iron-Air Grid Resilience Pilot",
        agency="NYSERDA",
        agency_code="NYSERDA",
        target_funding=3000000.0,
        total_budget=4000000.0,
        cost_share_pct=25.0,
        stage="draft",
        stage_label="Draft",
        is_won=False,
        recipient_name="Grid Storage Tech Inc",
        tech_area="Energy Storage",
        description="A multi-day energy storage demonstration deployed in an Upstate Disadvantaged Community providing peak reliability.",
        sopo_tasks_json=[{"task": "Task 1.0: Permitting", "budget": "$600,000", "milestone": "M1.2", "gate": "G1", "trl": "TRL 5"}],
        rubric_scores_json=[
            {"criterion": "Technical Innovation & Advancement", "max_pts": 30, "score": 25, "feedback": "Good baseline."},
            {"criterion": "Work Plan & Feasibility", "max_pts": 30, "score": 26, "feedback": "Solid milestone pacing."},
            {"criterion": "Commercialization & Impact", "max_pts": 40, "score": 35, "feedback": "Strong market demand."}
        ]
    )
    db_session.merge(test_prop)
    db_session.commit()

    resp = client.post(
        f"/api/proposals/{test_prop.id}/red-team",
        json={"review_notes": "Evaluate rigorously for NYSERDA Round 3 storage."}
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "success"
    assert data["red_team_score"] > 50
    assert data["stage"] == "red_team"
    assert data["stage_label"] == "Red-Team Audited"
    assert "rubric_scores" in data
    assert len(data["rubric_scores"]) >= 3

def test_proposal_red_team_llm_mock(db_session):
    """Test proposal red-team audit with LLM mock output."""
    test_prop = Proposal(
        id="prop-test-red-team-002",
        solicitation_number="DE-FOA-0002900",
        title="Next-Gen Solid State Battery Module",
        agency="U.S. Department of Energy",
        agency_code="DOE",
        target_funding=4000000.0,
        total_budget=5000000.0,
        cost_share_pct=20.0,
        stage="draft",
        stage_label="Draft",
        is_won=False,
        recipient_name="Solid State Energy Labs",
        tech_area="Energy Storage",
        description="Developing high-nickel cathode solid electrolyte cells.",
        sopo_tasks_json=[],
        rubric_scores_json=[]
    )
    db_session.merge(test_prop)
    db_session.commit()

    mock_audit = {
        "red_team_score": 93.5,
        "executive_feedback": "Highly compelling technical narrative with strong commercialization runway.",
        "rubric_scores": [
            {"criterion": "Technical Merit & Innovation", "max_pts": 40, "score": 38, "feedback": "Novel solid interface."},
            {"criterion": "Work Breakdown Structure & Feasibility", "max_pts": 30, "score": 28, "feedback": "Well structured Go/No-Go gates."},
            {"criterion": "Commercialization & Market Adoption", "max_pts": 30, "score": 27.5, "feedback": "Letters of intent present."}
        ],
        "fatal_flaws": ["Need deeper baseline thermal runaway analysis."],
        "key_differentiators": ["3x energy density over standard NMC811."]
    }

    with patch("app.api.proposals.settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.gemini_api_key = ""
        mock_settings.anthropic_api_key = ""
        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client
            mock_resp = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = json.dumps(mock_audit)
            mock_resp.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_resp

            audit_res = _run_red_team_audit_with_llm(test_prop, "Focus on automotive standards")
            assert audit_res["red_team_score"] == 93.5
            assert len(audit_res["rubric_scores"]) == 3
            assert audit_res["key_differentiators"][0] == "3x energy density over standard NMC811."

# ==============================================================================
# COMPONENT 3: ADMIN EMAIL SUMMARIZER & REPLY DRAFTER TESTS
# ==============================================================================

def test_conversation_summarizer_and_draft_reply(db_session):
    """Test contact conversation summarization and contextual reply drafting."""
    contact = Contact(
        id=7788,
        name_display="Sarah Jenkins",
        title="VP of Technology",
        institution_name="Apex Clean Energy Labs",
        email="sjenkins@apexcleanenergy.com",
        technology_area="Energy Storage"
    )
    db_session.merge(contact)
    db_session.commit()

    thread = ContactEmailThread(
        id=5566,
        contact_id=contact.id,
        contact_email=contact.email,
        contact_name=contact.name_display,
        institution_name=contact.institution_name,
        technology_area=contact.technology_area,
        status="pending_reply",
        total_messages=2,
        inbound_count=1,
        outbound_count=1
    )
    db_session.merge(thread)
    db_session.commit()

    msg1 = ContactEmailMessage(
        id=101,
        thread_id=thread.id,
        contact_id=contact.id,
        direction="outbound",
        from_email="bowens@aixenergy.io",
        to_email=contact.email,
        subject="Clean Energy Funding Intelligence Terminal Invitation",
        body_text="Hi Sarah, inviting you to test our clean energy innovation database."
    )
    msg2 = ContactEmailMessage(
        id=102,
        thread_id=thread.id,
        contact_id=contact.id,
        direction="inbound",
        from_email=contact.email,
        to_email="bowens@aixenergy.io",
        subject="Re: Clean Energy Funding Intelligence Terminal Invitation",
        body_text="Hi Brandon, thanks for reaching out. We are actively looking for NYSERDA storage grants and would love to schedule a quick call next Tuesday."
    )
    db_session.merge(msg1)
    db_session.merge(msg2)
    db_session.commit()

    summary_res = summarize_conversation_thread(db_session, thread.id)
    assert summary_res["thread_id"] == thread.id
    assert "summary" in summary_res
    assert len(summary_res["summary"]) > 10
    assert "sentiment" in summary_res
    assert "next_action" in summary_res
    assert "takeaways" in summary_res
    assert "suggested_reply_draft" in summary_res
    assert len(summary_res["suggested_reply_draft"]) > 10

def test_admin_email_draft_reply_endpoint(db_session):
    """Test POST /api/admin/email/threads/{id}/draft-reply endpoint."""
    contact = Contact(
        id=7789,
        name_display="David Miller",
        title="Director of Federal Affairs",
        institution_name="Hydrogen Power Systems",
        email="dmiller@h2powersystems.com",
        technology_area="Clean Hydrogen"
    )
    db_session.merge(contact)
    db_session.commit()

    thread = ContactEmailThread(
        id=5567,
        contact_id=contact.id,
        contact_email=contact.email,
        contact_name=contact.name_display,
        institution_name=contact.institution_name,
        technology_area=contact.technology_area,
        status="pending_reply",
        total_messages=1,
        inbound_count=1,
        outbound_count=0
    )
    db_session.merge(thread)
    db_session.commit()

    msg = ContactEmailMessage(
        id=103,
        thread_id=thread.id,
        contact_id=contact.id,
        direction="inbound",
        from_email=contact.email,
        to_email="bowens@aixenergy.io",
        subject="Teaming on DOE Regional Clean Hydrogen Hubs",
        body_text="Brandon, we want to team on the upcoming Appalachian hydrogen hub grant. What data do you have on past winners?"
    )
    db_session.merge(msg)
    db_session.commit()

    resp = client.post(f"/api/admin/email/threads/{thread.id}/draft-reply")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "ok"
    assert data["thread_id"] == thread.id
    assert data["contact_name"] == "David Miller"
    assert "body_text" in data
    assert len(data["body_text"]) > 20
    assert "subject" in data

