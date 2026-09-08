"""Strategy API endpoints."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.community import Strategy
from app.api.community import require_creator_hash, get_creator_hash
from app.engine.strategy import ProjectSponsorStrategy, FundingOrgStrategy
from pydantic import BaseModel
import datetime
from io import BytesIO

router = APIRouter()

class StrategyCreate(BaseModel):
    mode: str
    title: Optional[str] = None
    inputs_json: Dict[str, Any]

class StrategyUpdate(BaseModel):
    inputs_json: Dict[str, Any]

class DirectExecuteRequest(BaseModel):
    mode: str  # "project_sponsor" or "funding_organization"
    title: Optional[str] = None
    inputs: Dict[str, Any]


@router.get("/strategy/templates")
def get_strategy_templates():
    """Returns institutional pre-configured strategy templates for both Sponsor and Funder modes."""
    return {
        "project_sponsor_templates": [
            {
                "id": "iron_air_ldes",
                "name": "Iron-Air 100-Hour Long-Duration Storage System",
                "sector": "Energy Storage & Long-Duration Storage",
                "technology": "Iron-Air Battery",
                "fuel_vector": "Clean Electricity / Thermal",
                "current_trl": 5,
                "target_trl": 8,
                "sponsor_type": "Early-Stage Hardtech Developer",
                "state": "New York",
                "target_agency": "NYSERDA",
                "budget": "$10,000,000",
                "cost_share_pct": "20%",
                "technical_bottlenecks": [
                    "Air-breathing cathode degradation during multi-day continuous discharge",
                    "Parasitic hydrogen evolution reaction at iron anode requiring high coulombic efficiency",
                    "Balance-of-plant thermal management during sub-zero ambient winter extremes"
                ]
            },
            {
                "id": "solid_oxide_h2",
                "name": "High-Temperature Solid Oxide Electrolyzer (SOEC) Scale-Up",
                "sector": "Clean Hydrogen & Synthetic Fuels",
                "technology": "Solid Oxide Electrolyzer (SOEC)",
                "fuel_vector": "Hydrogen (H2) & Derivatives",
                "current_trl": 4,
                "target_trl": 7,
                "sponsor_type": "University & OEM Consortium",
                "state": "California",
                "target_agency": "DOE",
                "budget": "$15,000,000",
                "cost_share_pct": "20%",
                "technical_bottlenecks": [
                    "Chromium poisoning at oxygen electrode under 750C operation",
                    "Stack seal degradation and thermal cycling mechanical stresses",
                    "Stack manufacturing yield and catalyst coating cost reduction"
                ]
            },
            {
                "id": "advanced_smr_heat",
                "name": "Small Modular Reactor (SMR) High-Temperature Industrial Process Heat",
                "sector": "Advanced Nuclear & Novel Generation",
                "technology": "High-Temperature Gas-Cooled SMR",
                "fuel_vector": "Thermal Steam / High-Grade Heat",
                "current_trl": 5,
                "target_trl": 8,
                "sponsor_type": "Corporate Prime & Lab Consortium",
                "state": "Federal / Multi-State",
                "target_agency": "DOE",
                "budget": "$40,000,000",
                "cost_share_pct": "50%",
                "technical_bottlenecks": [
                    "High-temperature intermediate heat exchanger alloy corrosion",
                    "Secondary steam loop integration with industrial chemical manufacturing facility",
                    "Passive safety actuation verification during grid loss-of-load transients"
                ]
            }
        ],
        "funding_org_templates": [
            {
                "id": "nyserda_grid_flex_pon",
                "name": "Statewide Grid Flexibility & Long-Duration Storage Commercialization PON",
                "org_name": "NYSERDA",
                "org_type": "State Energy Office (NYSERDA, CEC, MassCEC)",
                "mandate": "Achieve 6 GW storage by 2030 and 100% zero-emission electricity by 2040 under NY CLCPA",
                "tech_focus": ["Energy Storage & Long-Duration Chemistries (LDES)", "Grid Modernization, Dynamic Line Rating & Transmission"],
                "program_length_years": "5 Years (Standard Multi-Phase Pathway)",
                "annual_award_distribution": "5 Awards/Year (25 Total Awards across 5-Year Pathway)",
                "program_philosophy": "Accelerate high-risk, high-TRL-gain hardtech breakthroughs by establishing mandatory utility testbed hosting, empirical milestone phase-gating, and non-federal cost-share alignment.",
                "program_pool": "$25,000,000",
                "award_cap": "$4,000,000",
                "target_trl_min": 4,
                "target_trl_max": 8,
                "solicitation_instrument": "3-Stage Competitive RFP with Go/No-Go Milestone Gates"
            },
            {
                "id": "arpa_e_transformational_fuels",
                "name": "Transformational Zero-Carbon Aviation & Maritime Fuel Synthesis FOA",
                "org_name": "US Department of Energy (DOE)",
                "org_type": "Federal Advanced Research Agency (DOE, ARPA-E, NSF)",
                "mandate": "Federal Energy Earthshots: $1/kg clean hydrogen, $20/kWh 10hr+ storage, and <$100/ton DAC by 2030",
                "tech_focus": ["Clean Hydrogen, Ammonia & Sustainable E-Fuels", "Carbon Management, Direct Air Capture & Storage"],
                "program_length_years": "3 Years (Accelerated Pilot & Feasibility Pathway)",
                "annual_award_distribution": "Ramped: 10 Phase-1 feasibility -> 4 Phase-2 pilot -> 2 Phase-3 host demos/yr",
                "program_philosophy": "Bridge the hardtech commercialization 'Valley of Death' (TRL 4-7) through standardized testing protocols, third-party lab verification, and reciprocal state-federal co-funding.",
                "program_pool": "$45,000,000",
                "award_cap": "$6,000,000",
                "target_trl_min": 3,
                "target_trl_max": 7,
                "solicitation_instrument": "Accelerated Open FOA with Stage-Gated Down-Selection"
            },
            {
                "id": "utility_der_resilience",
                "name": "Distribution Feeder Resilience & Microgrid Hosting Capacity Sandbox",
                "org_name": "Regulated Electric & Gas Utility (ConEd / National Grid)",
                "org_type": "Regulated Electric & Gas Utility (ConEd, National Grid)",
                "mandate": "Utility Grid Modernization: Substation CapEx deferral, EV peak shaving, and feeder hosting capacity",
                "tech_focus": ["Grid Modernization, Dynamic Line Rating & Transmission", "Energy Storage & Long-Duration Chemistries (LDES)"],
                "program_length_years": "5 Years (Decadal Reliability Blueprint)",
                "annual_award_distribution": "Even Cadence: 4 High-Cap Anchor Awards/Year ($2M-$5M each)",
                "program_philosophy": "Fund modular, rapidly deployable grid-edge flexibility solutions that defer utility substation CapEx and resolve near-term transmission interconnection bottlenecks.",
                "program_pool": "$12,000,000",
                "award_cap": "$2,000,000",
                "target_trl_min": 5,
                "target_trl_max": 8,
                "solicitation_instrument": "Utility Sandbox Demonstration & Behind-the-Meter Pilot Program"
            }
        ]
    }


@router.post("/strategy/quick-execute")
def quick_execute_strategy(req: DirectExecuteRequest, db: Session = Depends(get_db)):
    """Runs instant database intelligence queries and OpenAI LLM synthesis directly."""
    if req.mode not in ["project_sponsor", "funding_organization", "sponsor", "funder"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'project_sponsor' or 'funding_organization'")
    
    canonical_mode = "project_sponsor" if req.mode in ["project_sponsor", "sponsor"] else "funding_organization"
    
    try:
        if canonical_mode == "project_sponsor":
            engine = ProjectSponsorStrategy(db, req.inputs)
            results = engine.execute()
        else:
            engine = FundingOrgStrategy(db, req.inputs)
            results = engine.execute()
            
        return {
            "status": "complete",
            "mode": canonical_mode,
            "title": req.title or results.get("title", "Strategic Research & Capital Plan"),
            "results": results,
            "executed_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy execution error: {str(e)}")


@router.post("/strategy")
def create_strategy(req: StrategyCreate, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    if req.mode not in ["project_sponsor", "funding_organization"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
        
    s = Strategy(
        creator_hash=creator_hash,
        mode=req.mode,
        title=req.title,
        inputs_json=req.inputs_json,
        status="draft"
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("/strategy/{strategy_id}")
def get_strategy(strategy_id: int, creator_hash: Optional[str] = Depends(get_creator_hash), db: Session = Depends(get_db)):
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s or s.deleted_at:
        raise HTTPException(404, "Strategy not found")
        
    if s.creator_hash != creator_hash:
        if not s.is_public or s.status != "complete":
            raise HTTPException(403, "Access denied")
            
    return s


@router.put("/strategy/{strategy_id}")
def update_strategy(strategy_id: int, req: StrategyUpdate, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s or s.deleted_at:
        raise HTTPException(404, "Strategy not found")
    if s.creator_hash != creator_hash:
        raise HTTPException(403, "Access denied")
        
    s.inputs_json = req.inputs_json
    db.commit()
    return s


@router.delete("/strategy/{strategy_id}")
def delete_strategy(strategy_id: int, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s:
        raise HTTPException(404, "Strategy not found")
    if s.creator_hash != creator_hash:
        raise HTTPException(403, "Access denied")
        
    s.deleted_at = datetime.datetime.utcnow()
    db.commit()
    return {"status": "deleted"}


@router.post("/strategy/{strategy_id}/execute")
def execute_strategy(strategy_id: int, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s or s.deleted_at:
        raise HTTPException(404, "Strategy not found")
    if s.creator_hash != creator_hash:
        raise HTTPException(403, "Access denied")
        
    s.status = "processing"
    db.commit()
    
    try:
        inputs = s.inputs_json or {}
        
        if s.mode == "project_sponsor":
            strat_engine = ProjectSponsorStrategy(db, inputs)
            results = strat_engine.execute()
        else:
            strat_engine = FundingOrgStrategy(db, inputs)
            results = strat_engine.execute()

        s.status = "complete"
        s.results_json = results
        s.report_json = {
            "narrative": results.get("executive_thesis") or results.get("program_blueprint_narrative", ""),
            "title": results.get("title", s.title or "Strategy Plan")
        }
        s.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(s)
        return s
    except Exception as e:
        s.status = "failed"
        s.results_json = {"error": str(e)}
        db.commit()
        raise HTTPException(500, detail=f"Strategy execution error: {e}")


@router.get("/strategy")
def list_strategies(
    mode: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Strategy).filter(Strategy.status == "complete", Strategy.is_public == True, Strategy.deleted_at == None)
    
    if mode:
        query = query.filter(Strategy.mode == mode)
    if search:
        query = query.filter(Strategy.title.ilike(f"%{search}%"))
        
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/strategy/{strategy_id}/pdf")
def export_strategy_pdf(strategy_id: int, db: Session = Depends(get_db)):
    """Exports a publication-grade PDF Executive Strategic Monograph."""
    from fpdf import FPDF
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s or s.deleted_at:
        raise HTTPException(404, "Strategy not found")
        
    res = s.results_json or {}
class ExportPdfRequest(BaseModel):
    results: Dict[str, Any]
    title: Optional[str] = None
    mode: Optional[str] = "project_sponsor"


def _clean_text(s: Any) -> str:
    """Cleans HTML tags and replaces non-latin1 characters for FPDF."""
    if s is None:
        return ""
    txt = str(s)
    # Remove HTML tags
    txt = txt.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    txt = txt.replace("<strong>", "").replace("</strong>", "").replace("<em>", "").replace("</em>", "")
    # Normalize unicode punctuation for helvetica
    txt = txt.replace("\u2013", "-").replace("\u2014", "--").replace("\u2018", "'").replace("\u2019", "'")
    txt = txt.replace("\u201c", '"').replace("\u201d", '"').replace("\u2022", "*").replace("\u2192", "->")
    # Encode/decode to latin-1 safe characters
    return txt.encode("latin-1", "replace").decode("latin-1")


def generate_strategy_pdf_stream(res: Dict[str, Any], title: str, mode: str) -> BytesIO:
    """Generates a structured, multi-page publication-grade PDF Strategic Plan."""
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # ─── HEADER / BANNER ───────────────────────────────────────────────
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "ENERGY INNOVATION TERMINAL", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(79, 70, 229)
    mode_label = "PROJECT SPONSOR RESEARCH & CAPITAL STRATEGY" if mode == "project_sponsor" else "FUNDING ORGANIZATION PROGRAM BLUEPRINT"
    pdf.cell(0, 6, f"EXECUTIVE STRATEGIC PLAN | {mode_label}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(5)
    
    # ─── DOCUMENT TITLE ────────────────────────────────────────────────
    pdf.set_font("helvetica", "B", 15)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 7, _clean_text(title))
    pdf.ln(3)
    
    # ─── METADATA SUMMARY BOX ──────────────────────────────────────────
    tech_prof = res.get("technology_profile") or {}
    org_prof = res.get("org_profile") or {}
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(10, pdf.get_y(), 190, 22, style="FD")
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_xy(12, pdf.get_y() + 2)
    
    if mode == "project_sponsor":
        tech_name = _clean_text(tech_prof.get("name", "Clean Tech"))
        fuel_vec = _clean_text(tech_prof.get("fuel_vector", "Clean Electricity"))
        c_trl = tech_prof.get("current_trl", 5)
        t_trl = tech_prof.get("target_trl", 8)
        
        pdf.cell(90, 5, f"Technology: {tech_name}", new_x="RIGHT")
        pdf.cell(90, 5, f"Fuel/Carrier Vector: {fuel_vec}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(12)
        pdf.cell(90, 5, f"Stage Progression: TRL {c_trl} -> TRL {t_trl}", new_x="RIGHT")
        pdf.cell(90, 5, f"Grounded Datastore: 54,300+ Historical Grants Tracked", new_x="LMARGIN", new_y="NEXT")
    else:
        o_name = _clean_text(org_prof.get("name", "Funding Agency"))
        o_type = _clean_text(org_prof.get("type", "State Energy Office"))
        p_pool = _clean_text(org_prof.get("program_pool", "$25M"))
        a_cap = _clean_text(org_prof.get("award_cap", "$4M"))
        p_len = _clean_text(org_prof.get("program_length_years", "5 Years"))
        a_dist = _clean_text(org_prof.get("annual_award_distribution", "5 Awards/Year"))
        
        pdf.cell(90, 5, f"Organization: {o_name} ({o_type})", new_x="RIGHT")
        pdf.cell(90, 5, f"Program Timeline: {p_len}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(12)
        pdf.cell(90, 5, f"Total Pool: {p_pool} | Cap: {a_cap}", new_x="RIGHT")
        pdf.cell(90, 5, f"Cadence: {a_dist[:38]}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_y(pdf.get_y() + 8)
    pdf.ln(4)
    
    # ─── SECTION 1: EXECUTIVE STRATEGIC THESIS ─────────────────────────
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "1. Executive Strategic Thesis & Positioning Narrative", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    narrative = res.get("executive_thesis") or res.get("program_blueprint_narrative") or "Strategic briefing synthesized from proprietary database facts."
    pdf.set_x(10)
    pdf.multi_cell(w=190, h=5.5, text=_clean_text(narrative), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # ─── SECTION 2: WORKSTREAM / SOLICITATION DECOMPOSITION ────────────
    if mode == "project_sponsor" and res.get("workstream_decomposition"):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7, "2. Milestone-Gated R&D Workstream Decomposition", new_x="LMARGIN", new_y="NEXT")
        
        for ws in res.get("workstream_decomposition", []):
            pdf.set_fill_color(241, 245, 249)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(30, 41, 59)
            phase_hdr = f"{_clean_text(ws.get('phase'))}  [{_clean_text(ws.get('trl_progression'))}] - Est. Budget: {_clean_text(ws.get('estimated_budget'))}"
            pdf.set_x(10)
            pdf.cell(190, 6, phase_hdr, fill=True, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("helvetica", "", 8.5)
            pdf.set_text_color(71, 85, 105)
            pdf.set_x(10)
            pdf.multi_cell(w=190, h=5, text=f"Objective: {_clean_text(ws.get('objective'))}", new_x="LMARGIN", new_y="NEXT")
            
            delivs = ws.get("deliverables", [])
            if delivs:
                deliv_str = "Key Deliverables: " + " | ".join([_clean_text(d) for d in delivs])
                pdf.set_x(10)
                pdf.multi_cell(w=190, h=4.5, text=deliv_str, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        pdf.ln(3)
        
    elif mode == "funding_organization":
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7, "2. Long-Term Research Pathway & Stage-Gated Solicitation Architecture", new_x="LMARGIN", new_y="NEXT")
        
        # Pathway Roadmap
        pw = res.get("program_pathway_timeline") or {}
        if pw.get("milestone_roadmap"):
            pdf.set_font("helvetica", "B", 9.5)
            pdf.set_text_color(79, 70, 229)
            pdf.set_x(10)
            pdf.cell(190, 6, f"Multi-Year Pathway Roadmap ({_clean_text(pw.get('total_years', '5 Years'))}) - {_clean_text(pw.get('annual_distribution_summary', ''))}", new_x="LMARGIN", new_y="NEXT")
            for rm in pw.get("milestone_roadmap", []):
                pdf.set_font("helvetica", "B", 8.5)
                pdf.set_text_color(30, 41, 59)
                pdf.set_x(10)
                pdf.cell(190, 5, f"* {_clean_text(rm.get('timeframe'))}: {_clean_text(rm.get('awards_target'))}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(71, 85, 105)
                pdf.set_x(10)
                pdf.multi_cell(w=190, h=4.5, text=f"   Focus: {_clean_text(rm.get('focus'))} | Gate: {_clean_text(rm.get('gate_criterion'))}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            pdf.ln(2)

        sol = res.get("solicitation_structure", {})
        for ph in sol.get("phases", []):
            pdf.set_fill_color(241, 245, 249)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(10)
            pdf.cell(190, 6, f"{_clean_text(ph.get('phase_name'))} ({_clean_text(ph.get('duration'))}) - Award: {_clean_text(ph.get('award_range'))}", fill=True, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("helvetica", "", 8.5)
            pdf.set_text_color(71, 85, 105)
            pdf.set_x(10)
            pdf.multi_cell(w=190, h=5, text=f"Go/No-Go Gate: {_clean_text(ph.get('go_no_go_milestone'))}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        pdf.ln(3)
        
    # ─── SECTION 3: CAPITAL STACKING / WHITESPACE ──────────────────────
    if mode == "project_sponsor" and res.get("capital_stacking_strategy"):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7, "3. Multi-Agency Non-Dilutive Capital Stacking Matrix", new_x="LMARGIN", new_y="NEXT")
        
        for cap in res.get("capital_stacking_strategy", []):
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(79, 70, 229)
            pdf.set_x(10)
            pdf.cell(60, 5, _clean_text(cap.get("layer")), new_x="RIGHT")
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(80, 5, _clean_text(cap.get("target_program")), new_x="RIGHT")
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(16, 185, 129)
            pdf.cell(50, 5, _clean_text(cap.get("estimated_amount")), new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("helvetica", "", 8.5)
            pdf.set_text_color(100, 116, 139)
            pdf.set_x(10)
            pdf.multi_cell(w=190, h=4.5, text=f"Match: {_clean_text(cap.get('cost_share_required'))} | Strategic Utility: {_clean_text(cap.get('strategic_utility'))}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.5)
        pdf.ln(3)
        
    # ─── SECTION 4: HISTORICAL AWARDS COMPS ────────────────────────────
    if res.get("historical_award_comps"):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 7, "4. Empirical Peer Award Benchmarks (U.S. Energy Innovation Database)", new_x="LMARGIN", new_y="NEXT")
        
        for a in res.get("historical_award_comps", [])[:5]:
            pdf.set_font("helvetica", "B", 8.5)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(10)
            pdf.cell(130, 5, _clean_text(a.get("project_title"))[:70], new_x="RIGHT")
            pdf.set_font("helvetica", "B", 8.5)
            pdf.set_text_color(16, 185, 129)
            pdf.cell(60, 5, _clean_text(a.get("award_amount_fmt")), new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("helvetica", "", 8)
            pdf.set_text_color(100, 116, 139)
            pdf.set_x(10)
            pdf.cell(190, 4, f"Recipient: {_clean_text(a.get('recipient_name'))} ({_clean_text(a.get('recipient_type'))}) | Agency: {_clean_text(a.get('agency'))} ({a.get('year')})", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.5)
        pdf.ln(3)

    # ─── FOOTER & PROVENANCE ───────────────────────────────────────────
    pdf.ln(4)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 5, f"Report Generated: {datetime.datetime.utcnow().strftime('%B %d, %Y')} | Independent Decision-Support Terminal by Brandon N. Owens", new_x="LMARGIN", new_y="NEXT")
    
    buffer = BytesIO()
    pdf_bytes = pdf.output()
    buffer.write(pdf_bytes)
    buffer.seek(0)
    return buffer


@router.post("/strategy/export-pdf")
def export_strategy_direct_pdf(req: ExportPdfRequest):
    """Exports a publication-grade PDF Strategic Plan directly from the provided results payload."""
    title = req.title or req.results.get("title", "Strategic Research & Capital Plan")
    mode = req.mode or req.results.get("mode", "project_sponsor")
    buffer = generate_strategy_pdf_stream(req.results, title, mode)
    
    clean_filename = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
    clean_filename = clean_filename.replace(" ", "_")[:50] or "strategy_plan"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}.pdf"}
    )


@router.post("/strategy/{strategy_id}/pdf")
@router.get("/strategy/{strategy_id}/pdf")
def export_strategy_pdf(strategy_id: int, db: Session = Depends(get_db)):
    """Exports a publication-grade PDF Strategic Plan for a stored strategy."""
    s = db.query(Strategy).filter_by(id=strategy_id).first()
    if not s or s.deleted_at:
        raise HTTPException(404, "Strategy not found")
        
    res = s.results_json or {}
    mode = s.mode
    title = s.title or res.get("title", "Strategic Research & Capital Plan")
    buffer = generate_strategy_pdf_stream(res, title, mode)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=strategy_{strategy_id}.pdf"}
    )


