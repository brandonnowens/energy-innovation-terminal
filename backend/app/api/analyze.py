import os
import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.opportunity import Opportunity
from app.engine.analyzer import analyze_project
from app.engine.document_extractor import extract_multiple_documents
from app.engine.project_doc_analyzer import analyze_project_documents
from app.engine.profile import ProjectProfile
from app.engine.llm_opportunity_matcher import analyze_opportunity_fit_with_llm
from app.engine.advisor_qc import evaluate_opportunity_with_advisor_qc
from app.engine.winning_angle_engine import generate_winning_angle_with_llm

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Project analysis request."""
    text: str = Field("", description="Project description (optional free text)")
    applicant_type: Optional[str] = None
    location: Optional[str] = None
    trl: Optional[int] = Field(None, ge=1, le=9)
    cost: Optional[float] = None
    timeline: Optional[str] = None
    partners: Optional[str] = None
    # Structured multi-select fields
    technology_areas: Optional[list[str]] = None
    activity_types: Optional[list[str]] = None
    sectors: Optional[list[str]] = None
    fuel_types: Optional[list[str]] = None
    agencies: Optional[list[str]] = None


class CapitalStackRequest(BaseModel):
    """Interactive capital stack waterfall calculation request."""
    project_cost: float = Field(10_000_000.0, description="Total project capital expenditure ($)")
    matched_grant_max: Optional[float] = None
    technology_category: Optional[str] = None
    technology_areas: Optional[list[str]] = None
    activity_types: Optional[list[str]] = None
    project_summary: Optional[str] = None
    applicant_type: Optional[str] = None
    solicitation_name: Optional[str] = None
    agency: Optional[str] = None
    energy_community_bonus: bool = True
    domestic_content_bonus: bool = False
    prevailing_wage_compliant: bool = True
    tax_exempt_direct_pay: Optional[bool] = None


class TestConnectionRequest(BaseModel):
    """LLM provider connection verification request."""
    provider: str = "openai"
    api_key: Optional[str] = None
    model: Optional[str] = "gpt-4o"
    save_key: bool = True


class OpportunityLLMRequest(BaseModel):
    """On-demand opportunity LLM diligence request."""
    opportunity_id: int
    project_profile: Optional[Dict[str, Any]] = None
    force_refresh: bool = False


class WinningAngleRequest(BaseModel):
    """Request payload for reverse-engineering the winning angle & rubric."""
    opportunity_id: Optional[Any] = None
    solicitation_number: Optional[str] = None
    opportunity_name: Optional[str] = None
    agency: Optional[str] = None
    project_profile: Optional[Dict[str, Any]] = None
    match_score: Optional[float] = 0.85
    force_live: bool = False


@router.get("/analyze/llm-status")
@router.get("/llm/status")
def get_llm_status():
    """Returns the current configuration and connection status of OpenAI and other LLM providers."""
    openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
    anthropic_key = getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY")

    return {
        "openai": {
            "configured": bool(openai_key),
            "masked_key": f"...{openai_key[-4:]}" if openai_key and len(openai_key) >= 4 else None,
            "default_model": "gpt-4o",
        },
        "gemini": {
            "configured": bool(gemini_key),
            "masked_key": f"...{gemini_key[-4:]}" if gemini_key and len(gemini_key) >= 4 else None,
            "default_model": "gemini-2.5-flash",
        },
        "anthropic": {
            "configured": bool(anthropic_key),
            "masked_key": f"...{anthropic_key[-4:]}" if anthropic_key and len(anthropic_key) >= 4 else None,
            "default_model": "claude-3-5-sonnet-20241022",
        },
        "active_provider": "openai" if openai_key else ("gemini" if gemini_key else "grounded_offline"),
    }


@router.post("/analyze/test-connection")
def test_connection_endpoint(req: TestConnectionRequest):
    """
    Tests live connectivity with OpenAI (or Gemini / Anthropic), validates model availability,
    and optionally saves the API key to application settings.
    """
    prov = (req.provider or "openai").lower()

    if prov == "openai":
        key = req.api_key.strip() if req.api_key else (getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY"))
        if not key:
            return {
                "connected": False,
                "provider": "openai",
                "message": "No OpenAI API key found. Please enter an OpenAI API key.",
            }
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            models_response = client.models.list()
            available = [m.id for m in models_response.data if any(prefix in m.id for prefix in ["gpt-4o", "gpt-4", "o1", "o3", "chatgpt"])]

            if req.save_key:
                settings.openai_api_key = key
                os.environ["OPENAI_API_KEY"] = key

            return {
                "connected": True,
                "provider": "openai",
                "model": req.model or "gpt-4o",
                "message": "Successfully connected to OpenAI! GPT-4o is active for document intelligence, summarization, and grant matching.",
                "available_models": available[:8],
                "masked_key": f"...{key[-4:]}" if len(key) >= 4 else "...",
            }
        except Exception as e:
            return {
                "connected": False,
                "provider": "openai",
                "message": f"Failed to connect to OpenAI: {str(e)}",
            }

    elif prov == "gemini":
        key = req.api_key.strip() if req.api_key else (getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY"))
        if not key:
            return {
                "connected": False,
                "provider": "gemini",
                "message": "No Gemini API key found. Please enter a Google Gemini API key.",
            }
        try:
            from google import genai
            client = genai.Client(api_key=key)
            client.models.generate_content(
                model=req.model or "gemini-2.5-flash",
                contents="ping",
            )
            if req.save_key:
                settings.gemini_api_key = key
                os.environ["GEMINI_API_KEY"] = key

            return {
                "connected": True,
                "provider": "gemini",
                "model": req.model or "gemini-2.5-flash",
                "message": "Successfully connected to Google Gemini!",
                "masked_key": f"...{key[-4:]}" if len(key) >= 4 else "...",
            }
        except Exception as e:
            return {
                "connected": False,
                "provider": "gemini",
                "message": f"Failed to connect to Gemini: {str(e)}",
            }

    elif prov == "anthropic":
        key = req.api_key.strip() if req.api_key else (getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY"))
        if not key:
            return {
                "connected": False,
                "provider": "anthropic",
                "message": "No Anthropic API key found. Please enter an Anthropic API key.",
            }
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            client.messages.create(
                model=req.model or "claude-3-5-sonnet-20241022",
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}],
            )
            if req.save_key:
                settings.anthropic_api_key = key
                os.environ["ANTHROPIC_API_KEY"] = key

            return {
                "connected": True,
                "provider": "anthropic",
                "model": req.model or "claude-3-5-sonnet-20241022",
                "message": "Successfully connected to Anthropic Claude!",
                "masked_key": f"...{key[-4:]}" if len(key) >= 4 else "...",
            }
        except Exception as e:
            return {
                "connected": False,
                "provider": "anthropic",
                "message": f"Failed to connect to Anthropic: {str(e)}",
            }

    return {
        "connected": False,
        "provider": prov,
        "message": f"Unknown provider: {prov}",
    }


@router.post("/analyze")
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze a project description and match against multi-agency opportunities (CEC, MassCEC, DOE, ARPA-E, NSF, NYSERDA, utilities)."""
    result = analyze_project(
        db=db,
        text=request.text,
        applicant_type=request.applicant_type,
        location=request.location,
        trl=request.trl,
        cost=request.cost,
        timeline=request.timeline,
        partners=request.partners,
        technology_areas=request.technology_areas,
        activity_types=request.activity_types,
        sectors=request.sectors,
        fuel_types=request.fuel_types,
        target_agencies=request.agencies,
    )
    return result


class ExtractTextRequest(BaseModel):
    """Project raw text extraction and characterization request."""
    text: str = Field(..., min_length=5, description="Project description or proposal text to characterize")
    api_key: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = "openai"


@router.post("/analyze/extract-text")
def extract_text_project_characterization(req: ExtractTextRequest):
    """
    Characterizes a project from raw text using OpenAI / LLM analysis,
    extracting structured technology areas, applicant type, TRL, budget, location,
    and selecting the top 3-6 most relevant funding organizations & utilities.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        analyzed_profile = analyze_project_documents(
            document_corpus=req.text,
            doc_metadata=[{"filename": "project_description.txt", "doc_type": "text"}],
            user_api_key=req.api_key,
            preferred_model=req.model,
            preferred_provider=req.provider,
        )
        return {
            "success": True,
            "extracted_profile": analyzed_profile,
            "engine_used": analyzed_profile.get("engine_used", "Project Characterization Engine"),
            "is_live_llm": analyzed_profile.get("is_live_llm", False),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project characterization failed: {str(e)}")


class SayYesMatrixRequest(BaseModel):
    project_title: Optional[str] = "Project Proposal"
    summary: Optional[str] = ""
    technology_areas: Optional[List[str]] = []
    location: Optional[str] = "NY"
    applicant_type: Optional[str] = "business"
    project_cost: Optional[float] = 5000000.0
    agencies: Optional[List[str]] = []
    limit: Optional[int] = 25


@router.post("/analyze/say-yes-matrix")
def get_say_yes_matrix(req: SayYesMatrixRequest, db: Session = Depends(get_db)):
    """
    Ranks the top 25 organizations and decision-maker contacts most likely to say 'yes'
    based on map capabilities, geographic service territories, and institutional pain points.
    """
    from app.engine.propensity_engine import rank_top_25_say_yes_matrix
    from app.engine.profile import ProjectProfile

    profile = ProjectProfile(
        project_title=req.project_title,
        summary=req.summary or req.project_title or "",
        technology_areas=req.technology_areas or [],
        target_location=req.location,
        location=req.location,
        applicant_type=req.applicant_type,
        project_cost=req.project_cost
    )

    ranked_matrix = rank_top_25_say_yes_matrix(
        db=db,
        profile=profile,
        target_agencies=req.agencies,
        limit=req.limit or 25
    )

    return {
        "success": True,
        "total_ranked": len(ranked_matrix),
        "say_yes_matrix": ranked_matrix
    }


@router.post("/analyze/upload-docs")
async def upload_and_extract_project_documents(
    files: List[UploadFile] = File(...),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
):
    """
    Uploads multi-format project files (DOCX, PDF, PPTX, XLSX, TXT) and uses an LLM
    to extract structured project characteristics and synthesize a comprehensive summary.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Read all uploaded file bytes
    file_tuples = []
    for f in files:
        content = await f.read()
        file_tuples.append((f.filename or "uploaded_doc", content))

    # Extract text and structure from each document
    extracted_corpus = extract_multiple_documents(file_tuples)

    if not extracted_corpus["combined_text"].strip():
        # Build specific error messages from documents
        doc_errors = [
            f"'{d.get('filename')}': {d.get('error') or 'no extractable text'}"
            for d in extracted_corpus["documents"]
            if d.get("status") == "error" or not d.get("text")
        ]
        error_msg = "Could not extract readable text from uploaded file(s). " + "; ".join(doc_errors)
        raise HTTPException(
            status_code=400,
            detail=error_msg,
        )

    # Run AI Analysis Engine (Gemini / OpenAI / Anthropic / Grounded Heuristics)
    try:
        analyzed_profile = analyze_project_documents(
            document_corpus=extracted_corpus["combined_text"],
            doc_metadata=extracted_corpus["documents"],
            user_api_key=api_key,
            preferred_model=model,
            preferred_provider=provider,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI document analysis failed: {str(e)}")

    return {
        "success": True,
        "extracted_profile": analyzed_profile,
        "documents": [
            {
                "filename": doc.get("filename"),
                "doc_type": doc.get("doc_type"),
                "file_size": doc.get("file_size"),
                "word_count": doc.get("word_count"),
                "page_count": doc.get("page_count"),
                "slide_count": doc.get("slide_count"),
                "sheet_count": doc.get("sheet_count"),
                "status": doc.get("status"),
            }
            for doc in extracted_corpus["documents"]
        ],
        "total_files": extracted_corpus["total_files"],
        "total_words": extracted_corpus["total_words"],
        "total_bytes": extracted_corpus["total_bytes"],
        "engine_used": analyzed_profile.get("engine_used", "Grounded AI Engine"),
        "is_live_llm": analyzed_profile.get("is_live_llm", False),
    }


@router.post("/analyze/upload-and-match")
async def upload_and_match_project(
    files: List[UploadFile] = File(...),
    agencies: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    1-Click pipeline: Upload project files, synthesize with LLM, and immediately
    run the full multi-agency matching and capital stack optimization pipeline.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    file_tuples = []
    for f in files:
        content = await f.read()
        file_tuples.append((f.filename or "uploaded_doc", content))

    extracted_corpus = extract_multiple_documents(file_tuples)

    if not extracted_corpus["combined_text"].strip():
        doc_errors = [
            f"'{d.get('filename')}': {d.get('error') or 'no extractable text'}"
            for d in extracted_corpus["documents"]
            if d.get("status") == "error" or not d.get("text")
        ]
        error_msg = "Could not extract readable text from uploaded file(s). " + "; ".join(doc_errors)
        raise HTTPException(status_code=400, detail=error_msg)

    # Run AI analysis
    analyzed_profile = analyze_project_documents(
        document_corpus=extracted_corpus["combined_text"],
        doc_metadata=extracted_corpus["documents"],
        user_api_key=api_key,
        preferred_model=model,
        preferred_provider=provider,
    )

    # Parse agencies filter if provided
    agency_list = None
    if agencies:
        try:
            agency_list = json.loads(agencies)
        except Exception:
            agency_list = [a.strip() for a in agencies.split(",") if a.strip()]

    if not agency_list and analyzed_profile.get("suggested_agencies"):
        agency_list = analyzed_profile["suggested_agencies"]

    # Execute matching
    match_result = analyze_project(
        db=db,
        text=analyzed_profile["summary"],
        applicant_type=analyzed_profile["applicant_type"],
        location=analyzed_profile["location"],
        trl=analyzed_profile["estimated_trl"],
        cost=analyzed_profile["estimated_cost"],
        timeline=analyzed_profile["timeline"],
        partners=", ".join(analyzed_profile.get("partners", [])),
        technology_areas=analyzed_profile["technology_areas"],
        activity_types=analyzed_profile["activity_types"],
        sectors=analyzed_profile["sectors"],
        fuel_types=analyzed_profile["fuel_types"],
        target_agencies=agency_list,
    )

    # Attach document provenance to result
    match_result["extracted_profile"] = analyzed_profile
    match_result["uploaded_documents"] = [
        {
            "filename": doc.get("filename"),
            "doc_type": doc.get("doc_type"),
            "file_size": doc.get("file_size"),
            "word_count": doc.get("word_count"),
        }
        for doc in extracted_corpus["documents"]
    ]

    return match_result


@router.post("/capital-stack")
def calculate_capital_stack_endpoint(request: CapitalStackRequest):
    """Calculates pro-forma capital stack waterfall with statutory IRA tax credits, grants, and blended WACC."""
    from app.engine.capital_stack_engine import calculate_capital_stack
    return calculate_capital_stack(
        project_cost=request.project_cost,
        matched_grant_max=request.matched_grant_max,
        technology_category=request.technology_category,
        technology_areas=request.technology_areas,
        activity_types=request.activity_types,
        project_summary=request.project_summary,
        applicant_type=request.applicant_type,
        solicitation_name=request.solicitation_name,
        agency=request.agency,
        energy_community_bonus=request.energy_community_bonus,
        domestic_content_bonus=request.domestic_content_bonus,
        prevailing_wage_compliant=request.prevailing_wage_compliant,
        tax_exempt_direct_pay=request.tax_exempt_direct_pay,
    )


@router.post("/analyze/export-pdf")
def export_project_analysis_pdf_endpoint(data: Dict[str, Any]):
    """
    Compiles and downloads a publication-grade PDF summary report of the project analysis,
    multi-agency grant matches, and Multi-Layer Financing / Blended WACC optimization.
    """
    import io
    from fastapi.responses import Response
    from app.engine.project_pdf_report import generate_project_analysis_pdf

    try:
        output_buffer = io.BytesIO()
        generate_project_analysis_pdf(data, output_buffer)
        pdf_bytes = output_buffer.getvalue()

        profile = data.get("extracted_profile") or data.get("structured_profile") or {}
        if isinstance(profile, str):
            import json
            try: profile = json.loads(profile)
            except Exception: profile = {}
        raw_title = profile.get("project_title") or profile.get("title") or "Clean_Energy_Project"
        clean_title = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in raw_title)[:40].strip('_')
        filename = f"{clean_title}_Match_and_Financing_Report.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate project summary PDF: {str(e)}")


@router.post("/analyze/opportunity-llm")
def analyze_opportunity_llm_endpoint(req: OpportunityLLMRequest, db: Session = Depends(get_db)):
    """
    Performs on-demand live OpenAI GPT-4o diligence for a specific funding opportunity and project profile.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == req.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity with ID {req.opportunity_id} not found")

    prof_data = req.project_profile or {}
    prof = ProjectProfile(
        project_title=prof_data.get("project_title") or prof_data.get("title") or "Clean Energy Innovation Project",
        summary=prof_data.get("summary") or "Clean energy infrastructure deployment project.",
        technology_areas=prof_data.get("technology_areas") or ["Clean Energy"],
        activity_types=prof_data.get("activity_types") or ["Demonstration"],
        sectors=prof_data.get("sectors") or ["Energy & Infrastructure"],
        fuel_types=prof_data.get("fuel_types") or ["Electricity"],
        estimated_trl=prof_data.get("estimated_trl") or prof_data.get("trl") or 5,
        applicant_type=prof_data.get("applicant_type") or "Commercial Entity",
        target_location=prof_data.get("target_location") or prof_data.get("location") or "New York",
        project_cost=float(prof_data.get("project_cost") or prof_data.get("estimated_cost") or 5_000_000.0),
    )

    result = analyze_opportunity_fit_with_llm(
        profile=prof,
        opp=opp,
        base_fit_score=0.85,
        force_live=req.force_refresh,
    )
    advisor_verdict = evaluate_opportunity_with_advisor_qc(
        profile=prof,
        opp=opp,
        force_live=req.force_refresh,
    )
    return {
        "opportunity_id": opp.id,
        "solicitation_number": opp.solicitation_number,
        "name": opp.name,
        "agency": opp.agency,
        "analysis": result,
        "advisor_qc": advisor_verdict.to_dict(),
    }


@router.post("/analyze/winning-angle")
def get_winning_angle_endpoint(req: WinningAngleRequest, db: Session = Depends(get_db)):
    """
    Reverse-engineers the reviewer scoring rubric, mandatory proposal keywords, optimal teaming partner roster,
    and high-scoring strategic narrative angle for a project/opportunity pair.
    """
    try:
        opp = None
        # 1. Try finding by numeric opportunity_id
        if req.opportunity_id is not None:
            try:
                opp_id_int = int(req.opportunity_id)
                opp = db.query(Opportunity).filter(Opportunity.id == opp_id_int).first()
            except (ValueError, TypeError):
                pass

        # 2. Try finding by solicitation number if opp not found
        if not opp and req.solicitation_number:
            opp = db.query(Opportunity).filter(Opportunity.solicitation_number.ilike(f"%{req.solicitation_number}%")).first()

        # 3. If still not found, construct synthetic opportunity from request parameters (e.g. for forecasting radar previews)
        if not opp:
            opp = Opportunity(
                id=999999,
                solicitation_number=req.solicitation_number or "SOLICITATION-PREVIEW",
                name=req.opportunity_name or "Clean Energy Funding Solicitation",
                agency=req.agency or "Public Agency",
                short_description="Clean energy research, development, and commercial demonstration grant solicitation.",
                total_funding=15000000.0,
                max_per_award=3000000.0,
            )

        prof_data = req.project_profile or {}

        # Safe cost parsing
        raw_cost = prof_data.get("project_cost") or prof_data.get("cost") or prof_data.get("estimated_cost") or 5_000_000.0
        if isinstance(raw_cost, (int, float)):
            cost_val = float(raw_cost)
        else:
            clean_num = "".join(c for c in str(raw_cost) if c.isdigit() or c == '.')
            try:
                cost_val = float(clean_num) if clean_num else 5_000_000.0
            except Exception:
                cost_val = 5_000_000.0

        # Safe TRL parsing
        raw_trl = prof_data.get("estimated_trl") or prof_data.get("trl") or 5
        if isinstance(raw_trl, (int, float)):
            trl_val = max(1, min(9, int(raw_trl)))
        else:
            clean_trl = "".join(c for c in str(raw_trl) if c.isdigit())
            try:
                trl_val = max(1, min(9, int(clean_trl[0]))) if clean_trl else 5
            except Exception:
                trl_val = 5

        # Safe technology parsing
        raw_techs = prof_data.get("technology_areas") or ["Clean Energy Innovation"]
        if isinstance(raw_techs, str):
            techs = [t.strip() for t in raw_techs.split(",") if t.strip()]
        elif isinstance(raw_techs, list):
            techs = [str(t) for t in raw_techs if t]
        else:
            techs = ["Clean Energy Innovation"]
        if not techs:
            techs = ["Clean Energy Innovation"]

        prof = ProjectProfile(
            project_title=str(prof_data.get("project_title") or prof_data.get("title") or "Clean Energy Innovation Project"),
            summary=str(prof_data.get("summary") or "Clean energy infrastructure deployment project."),
            technology_areas=techs,
            activity_types=prof_data.get("activity_types") or ["Demonstration"],
            sectors=prof_data.get("sectors") or ["Energy & Infrastructure"],
            fuel_types=prof_data.get("fuel_types") or ["Electricity"],
            estimated_trl=trl_val,
            applicant_type=str(prof_data.get("applicant_type") or "Commercial Entity"),
            target_location=str(prof_data.get("target_location") or prof_data.get("location") or "New York"),
            project_cost=cost_val,
        )

        report = generate_winning_angle_with_llm(
            db=db,
            profile=prof,
            opp=opp,
            match_score=req.match_score or 0.85,
            force_live=req.force_live,
        )
        return report.to_dict()
    except Exception as e:
        logger.error(f"Error in winning angle endpoint: {e}", exc_info=True)
        # Safe deterministic fallback on any error
        from app.engine.winning_angle_engine import generate_grounded_winning_angle
        safe_opp = Opportunity(
            id=999999,
            solicitation_number=req.solicitation_number or "SOL-PREVIEW",
            name=req.opportunity_name or "Funding Solicitation",
            agency=req.agency or "Funding Agency",
            short_description="Clean energy research and commercial demonstration grant solicitation.",
            total_funding=10000000.0,
        )
        safe_prof = ProjectProfile(
            project_title="Clean Energy Innovation Project",
            summary="Clean energy infrastructure deployment project.",
            technology_areas=["Clean Energy Innovation"],
            estimated_trl=5,
            project_cost=5000000.0,
        )
        safe_rep = generate_grounded_winning_angle(db, safe_prof, safe_opp, req.match_score or 0.85)
        return safe_rep.to_dict()
