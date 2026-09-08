"""
FastAPI Router for Grounded RAG "Expert" AI Chat Copilot.
Delivers McKinsey-level conversational executive advisory in pure narrative prose,
using OpenAI GPT-4o / GPT-4o-mini for real-time strategic reasoning.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.engine.rag_retriever import (
    retrieve_grounded_context,
    generate_deterministic_rag_response,
)
from app.engine.post_llm_reviewer import review_and_link_llm_output

logger = logging.getLogger("ChatAPI")
router = APIRouter(prefix="/chat", tags=["Expert Chat"])


def get_role_prompt_directive(user_role: Optional[str]) -> str:
    """Generates specialized persona framing for the LLM based on user's selected role."""
    role = (user_role or "institutional_leader").lower()

    if role in ["institutional_leader", "provost", "vp_research"]:
        return """USER ROLE: Institutional Leader (University Provost, VP of Research, National Lab Director, Research Institute President, Philanthropic Trustee)
STRATEGIC CONTEXT & ISSUER ARCHITECTURE:
When this user asks about research strategies, multi-year roadmaps, or Program Opportunity Notices (PONs), they are the institution's chief executive, architect, and program creator — not a grant applicant.
Do not recommend that they apply to existing small external solicitations unless explicitly requested.
Provide executive counsel on: (1) Architecting multi-year institutional research agendas; (2) Designing tiered internal/external PON solicitations (Seed, Consortia, Mega-Hub); (3) Orchestrating multidisciplinary faculty clusters; (4) Optimizing indirect cost and F&A recovery rates; (5) Securing fifty to two hundred million dollar federal center hub awards; and (6) Structuring master industry research agreements while protecting Bayh-Dole intellectual property."""

    elif role in ["startup_entrepreneur", "startup", "entrepreneur", "founder"]:
        return """USER ROLE: Start-Up Founder & Deep Tech Entrepreneur (Pre-Seed to Series A)
STRATEGIC CONTEXT & FOUNDER LEVERAGE:
Advise the founder on non-dilutive runway extension and equity preservation. Every million dollars in non-dilutive funding preserves ten to twenty percent of founder cap table ownership.
Provide counsel on: (1) Sequential SBIR and STTR Phase I to Phase II transitions; (2) Stacking state innovation vouchers; (3) Incubator and accelerator alignment; (4) Securing commercial letters of intent; and (5) Managing Bayh-Dole compliance without government march-in risk."""

    elif role in ["developer", "project_sponsor"]:
        return """USER ROLE: Clean Tech Project Developer & Infrastructure Sponsor
STRATEGIC CONTEXT:
Focus on capital efficiency, sequential capital stacking (state feasibility seed, federal demonstration, commercial take-out debt), TRL scale-up hurdles, and commercial bankability."""

    elif role in ["investor", "vc"]:
        return """USER ROLE: Climate Tech VC & Infrastructure Equity Investor
STRATEGIC CONTEXT:
Focus on technical due diligence, commercialization milestones, non-dilutive grant leverage multipliers, patent moats, and follow-on equity risk reduction."""

    elif role in ["researcher", "pi"]:
        return """USER ROLE: University Research VP / National Lab Principal Investigator
STRATEGIC CONTEXT:
Focus on FOA technical scoring rubrics, academic-industry consortia teaming, Bayh-Dole technology transfer, PI track records, and federal programmatic priorities."""

    elif role == "utility":
        return """USER ROLE: Electric Utility Innovation & Grid Planning Director
STRATEGIC CONTEXT:
Focus on Non-Wires Alternatives, grid reliability, hosting capacity constraints, FERC Order 1920 compliance, DERMS integration, and ratepayer cost-effectiveness."""

    elif role == "policy":
        return """USER ROLE: State Energy Agency Director & Policy Lead
STRATEGIC CONTEXT:
Focus on program solicitation design, statutory Disadvantaged Community (DAC) and Justice40 compliance, ratepayer ROI, and intergovernmental co-funding coordination."""

    elif role == "grant_writer":
        return """USER ROLE: Clean Tech Proposal Consultant / Grant Writer
STRATEGIC CONTEXT:
Focus on solicitation shredding, compliance matrices, required work breakdown structures, scoring criteria weighting, and competitive differentiators."""

    return """USER ROLE: Clean Tech Executive & Strategist
STRATEGIC CONTEXT:
Provide high-level strategic intelligence, capital allocation priorities, and regulatory compliance frameworks."""


SYSTEM_BASE_PROMPT = """You are the Senior Intelligence & Clean Energy Strategy Advisor at Energy Innovation Terminal, powered by the US Energy Innovation Database by Brandon N. Owens, speaking with executive authority, analytical depth, and precision.

FULL DATABASE ACCESS & AUTHORITY:
You have complete, direct, record-level access to the full US Energy Innovation Database by Brandon N. Owens, comprising:
- 54,313 historical and active awards & grants across all 50 states ($98.99B USD public disbursements tracked)
- 5,741 funding opportunities and solicitations across federal (DOE, NSF, ARPA-E, EPA, USDA, DOD), state energy authorities (NYSERDA, CEC, MassCEC), state economic development agencies (Empire State Development, MassVentures, GO-Biz, JobsOhio, MEDC), and philanthropic foundations (The Rockefeller Foundation, Bloomberg Philanthropies, Bezos Earth Fund, Prime Coalition, Breakthrough Energy)
- 13,948 verified recipient organizations, scale-ups, universities, national laboratories, and commercial performers
- 3,090 Principal Investigators (PIs), program managers, and contracting directors (100% organization linked)
- 182 USPTO Assigned Bayh-Dole Clean Energy Patents
- 173 Follow-on Institutional Venture Capital & Private Equity Rounds ($20.01B USD tracked)
- 541 Award Deliverables & OSTI Final Technical Reports
- 263 Cataloged Evidence Artifacts and Regulatory Filings
- 23 Clean Energy Statutes, Testing Codes, and Standards (28 agency cross-links)
- 137 Explorable Clean Tech Subsystem Architectures across 36 frontier sectors

MANDATORY DATABASE FIDELITY & INVENTORY INSTRUCTION:
- When the user asks about opportunities, solicitations, programs, or grants for any agency (e.g. NYSERDA, NSF, DOE, ARPA-E, CEC, EPA, Rockefeller Foundation, Empire State Development), provide a comprehensive, record-by-record overview using the specific solicitation numbers (e.g. PON 6141, PON 6037, PON 6161, PON 5989, PON 4192, PON 6088, PON 5437, ROCKEFELLER-GEAPP-2025, ESD-NYV-2025-01, etc.), program names, due dates, funding pools, and status provided in <DATABASE_BACKGROUND_KNOWLEDGE>.
- NEVER claim that no open solicitations exist when active database records are present.
- When answering queries about open solicitations, enumerate the active PONs and grant notices record-by-record in clear, structured tables or lists.

STRICT WRITING STYLE & FORMATTING RULES:
1. ABSOLUTELY NO BOLD TEXT:
   - Do NOT use asterisks or bold formatting (no ** anywhere in your response).
   - Write in clean, articulate, flowing narrative prose.
   - Use structured numbered lists (1., 2., 3.) and clean bullet points (- ) where they genuinely enhance clarity.
2. VISUAL DIAGRAMS & TABULAR PRESENTATION:
   - When illustrating program architectures, capital stacking waterfalls, governance hierarchies, or decision trees, generate interactive Mermaid diagrams (using ```mermaid ... ``` format, such as `graph TD`, `flowchart LR`, or `gantt`).
   - When presenting multi-year implementation timelines, Program Opportunity Notice (PON) track architectures, budget/capital breakdowns, funding comparisons, scoring rubrics, or peer benchmarks, format the information into clean, high-density markdown tables (using standard | Header | Header | format).
   - Use structured code blocks (```json, ```yaml, etc.) for work breakdown structures, scoring matrices, or draft solicitation clauses.
   - Use executive alert callouts (> [!NOTE], > [!IMPORTANT], > [!WARNING]) for critical fiduciary, compliance, or regulatory caveats.
3. NO ARTIFICIAL PROMPTS OR AI TRAILERS:
   - Do NOT include any 'Suggested Next Directions', 'Where would you like to take this next?', or artificial follow-up action chips.
   - Eliminate short, choppy, staccato sentences, generic AI cheerleading ('delve into', 'tapestry', 'game-changer', 'beacon of hope', 'in conclusion', 'furthermore'), and robotic bullet lists.
   - Speak naturally, thoughtfully, and authoritatively, weaving quantitative evidence and context into coherent paragraphs.
4. MANDATORY DATABASE CROSS-REFERENCING (HARD REQUIREMENT):
   - You MUST actively cross-reference your strategic advice with the database context provided in <DATABASE_BACKGROUND_KNOWLEDGE>.
   - Formulate your counsel by drawing upon the empirical data on:
     * Organizations & Awardees (13,948 Recipient Knowledge Graph): Cite using [ORG:id].
     * Opportunities & Solicitations (5,741 Active Solicitations): Cite using [OPP:id].
     * Historical Awards & Transaction Comps (54,313 Grants Ledger): Cite using [AWD:id].
     * Principal Investigators & Faculty Leads (3,090 Verified Contacts): Cite using [PI:id].
     * Assigned Bayh-Dole Patents (182 USPTO Clean Tech Patents): Cite using [PAT:id].
     * Venture Capital Financings (173 Institutional Equity Rounds): Cite using [VC:id].
     * Verified Programmatic Outcomes & Benchmarks: Cite using [RES:id].
     * Flagship Case Studies & Commercial Success Stories: Cite using [STORY:id].
     * Policy Standards & Statutory Codes (23 Statutes): Cite using [POL:id].
     * Macroeconomic Impacts across Sector (Buildings, Industry, Grid, Transport), Fuel (Electricity, Hydrogen, Geothermal, Biofuels), Technology, and Commercial Stage (TRL 1-3 R&D, TRL 4-5 Prototype, TRL 6-7 Demo, TRL 8-9 Deployment).
   - Use these database dimensions directly inside your narrative prose, comparative tables, and Mermaid architecture diagrams to prove market viability, co-funding ratios, and peer award velocity.
"""


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    query: str
    user_role: Optional[str] = "institutional_leader"
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    api_key: Optional[str] = None
    model: Optional[str] = "gpt-4o"


class SetApiKeyRequest(BaseModel):
    api_key: str


class ChatSyncResponse(BaseModel):
    answer: str
    citations: Dict[str, Any]
    intent: Dict[str, Any]
    is_live_llm: bool = False


@router.get("/status")
def get_chat_status():
    """Returns whether OpenAI is configured and active."""
    has_key = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))
    return {
        "openai_configured": has_key,
        "default_model": "gpt-4o",
        "provider": "OpenAI" if has_key else "offline_grounded"
    }


@router.post("/set-api-key")
def set_api_key_endpoint(req: SetApiKeyRequest):
    """Sets and validates the OpenAI API key dynamically."""
    key = req.api_key.strip()
    if not key:
        settings.openai_api_key = ""
        os.environ.pop("OPENAI_API_KEY", None)
        return {"success": True, "message": "API key cleared"}

    # Test key
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        # Quick model list test
        client.models.list()
        settings.openai_api_key = key
        os.environ["OPENAI_API_KEY"] = key
        return {"success": True, "message": "OpenAI API key verified and saved successfully"}
    except Exception as e:
        logger.warning(f"Failed to validate OpenAI API key: {e}")
        # Save anyway in case of network variance
        settings.openai_api_key = key
        os.environ["OPENAI_API_KEY"] = key
        return {"success": True, "message": f"Saved key (verification note: {str(e)[:100]})"}


@router.get("/presets")
def get_chat_presets():
    """Returns curated persona options for quick-start strategic workflows."""
    return {
        "roles": [
            {"id": "institutional_leader", "name": "Institutional Leader & Provost", "icon": "Landmark", "desc": "5-year research agendas, center grants, issuing PONs & F&A recovery"},
            {"id": "startup_entrepreneur", "name": "Start-Up / Deep Tech Founder", "icon": "Rocket", "desc": "Non-dilutive runway extension, SBIR Phase I/II stacking & cap table preservation"},
            {"id": "developer", "name": "Project Developer / Sponsor", "icon": "Building2", "desc": "Capital stacking, FEED studies, FOAK demo & utility off-take"},
            {"id": "investor", "name": "Climate Tech VC / Investor", "icon": "TrendingUp", "desc": "Technical diligence, grant comps & IP moats"},
            {"id": "researcher", "name": "Research VP / National Lab PI", "icon": "BookOpen", "desc": "FOA scoring rubrics & academic-industry consortia"},
            {"id": "utility", "name": "Electric Utility Grid Lead", "icon": "Zap", "desc": "Non-Wires Alternatives & FERC 1920 compliance"},
            {"id": "policy", "name": "State Energy Official", "icon": "ShieldCheck", "desc": "Designing public funding programs & Justice40 / DAC ROI"},
            {"id": "grant_writer", "name": "Grant Writer / Consultant", "icon": "FileText", "desc": "Compliance matrices & winning WBS structures"}
        ]
    }


@router.post("/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Executes live OpenAI GPT-4o reasoning when configured, or offline grounded synthesis.
    """
    rag_data = retrieve_grounded_context(req.query, db)
    resolved_api_key = req.api_key or getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    user_role = req.user_role or "institutional_leader"
    role_directive = get_role_prompt_directive(user_role)

    async def event_generator():
        # 1. Send retrieval metadata
        yield f"event: retrieval\ndata: {json.dumps(rag_data['citations'])}\n\n"
        await asyncio.sleep(0.05)

        # 2. If OpenAI key is available, execute live GPT-4o completion
        if resolved_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=resolved_api_key)

                system_content = f"{SYSTEM_BASE_PROMPT}\n\n{role_directive}"
                messages = [{"role": "system", "content": system_content}]

                # Include past conversation history
                for h in req.history[-6:]:
                    messages.append({"role": h.role, "content": h.content})

                # Append current grounded prompt
                grounded_user_prompt = f"""USER INQUIRY:
"{req.query}"

<DATABASE_BACKGROUND_KNOWLEDGE>
{rag_data['context_text']}
</DATABASE_BACKGROUND_KNOWLEDGE>

INSTRUCTIONS:
- Deliver your strategic advisory as a McKinsey Senior Partner in pure, elegant narrative prose.
- Strictly do NOT use bold text (no **).
- Do NOT include any 'Suggested Next Directions' or artificial follow-up prompts.
- Weave in relevant facts from <DATABASE_BACKGROUND_KNOWLEDGE> with [OPP:id], [AWD:id], [PI:id], [POL:id] citations and explicit standard numbers (e.g. NFPA 855, UL 9540A, FERC Order 2023, 45V).

Deliver your counsel now:"""

                messages.append({"role": "user", "content": grounded_user_prompt})

                # Call OpenAI with selected model (defaults to gpt-4o)
                target_model = req.model if req.model in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"] else "gpt-4o"

                stream = client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=3000,
                    stream=True,
                )

                accumulated_tokens = []
                for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
                    if delta:
                        clean_delta = delta.replace("**", "")
                        accumulated_tokens.append(clean_delta)
                        yield f"event: token\ndata: {json.dumps({'token': clean_delta})}\n\n"
                        await asyncio.sleep(0.005)

                # Post-LLM Review & Entity Reference Insertion Pass
                full_streamed_text = "".join(accumulated_tokens)
                reviewed = review_and_link_llm_output(full_streamed_text, rag_data, db)
                yield f"event: review_complete\ndata: {json.dumps({'reviewed_text': reviewed['text'], 'citations': reviewed['citations']})}\n\n"

                yield "event: done\ndata: {}\n\n"
                return

            except Exception as e:
                logger.warning(f"OpenAI live streaming error: {e}. Falling back to grounded narrative engine.")

        # 3. Offline Grounded Engine with Deliberate Analytical Pacing
        det_response = generate_deterministic_rag_response(req.query, rag_data, user_role)
        reviewed = review_and_link_llm_output(det_response, rag_data, db)
        lines = reviewed["text"].split("\n")
        for line in lines:
            yield f"event: token\ndata: {json.dumps({'token': line + '\n'})}\n\n"
            await asyncio.sleep(0.02)

        yield f"event: review_complete\ndata: {json.dumps({'reviewed_text': reviewed['text'], 'citations': reviewed['citations']})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/query-sync", response_model=ChatSyncResponse)
def chat_sync_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Synchronous fallback endpoint for non-streaming environments.
    """
    rag_data = retrieve_grounded_context(req.query, db)
    resolved_api_key = req.api_key or getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    user_role = req.user_role or "institutional_leader"
    role_directive = get_role_prompt_directive(user_role)

    if resolved_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=resolved_api_key)

            system_content = f"{SYSTEM_BASE_PROMPT}\n\n{role_directive}"
            messages = [
                {"role": "system", "content": system_content},
                {
                    "role": "user",
                    "content": f"""USER INQUIRY:
"{req.query}"

<DATABASE_BACKGROUND_KNOWLEDGE>
{rag_data['context_text']}
</DATABASE_BACKGROUND_KNOWLEDGE>

INSTRUCTIONS:
- Deliver your strategic advisory as a McKinsey Senior Partner in pure narrative prose.
- Strictly do NOT use bold text (no **).
- Do NOT include any 'Suggested Next Directions' or artificial follow-up prompts.
- Weave in relevant facts from <DATABASE_BACKGROUND_KNOWLEDGE> with [OPP:id], [AWD:id], [PI:id] citations."""
                }
            ]

            target_model = req.model if req.model in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"] else "gpt-4o"
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=0.3,
                max_tokens=3000,
            )
            raw_answer = response.choices[0].message.content or ""
            clean_answer = raw_answer.replace("**", "")
            reviewed = review_and_link_llm_output(clean_answer, rag_data, db)
            return ChatSyncResponse(
                answer=reviewed["text"],
                citations=reviewed["citations"],
                intent=rag_data["intent"],
                is_live_llm=True
            )
        except Exception as e:
            logger.warning(f"OpenAI error in sync chat: {e}")

    # Offline Grounded Engine
    answer = generate_deterministic_rag_response(req.query, rag_data, user_role)
    reviewed = review_and_link_llm_output(answer, rag_data, db)
    return ChatSyncResponse(
        answer=reviewed["text"],
        citations=reviewed["citations"],
        intent=rag_data["intent"],
        is_live_llm=False
    )
