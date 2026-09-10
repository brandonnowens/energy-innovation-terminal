"""
FastAPI Router for Tavus.io Conversational Video AI.
Enables real-time face-to-face AI video advisory sessions using Tavus Conversational Video Interface (CVI),
Daily.co WebRTC rooms, and grounded clean tech intelligence.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, and_

from app.database import get_db
from app.config import settings
from app.models.award import Award
from app.models.opportunity import Opportunity
from app.models.recipient import Recipient
from app.models.contact import Contact
from app.api.chat import get_role_prompt_directive
from app.engine.rag_retriever import retrieve_grounded_context, parse_query_intent, TECH_DOMAINS
from app.engine.post_llm_reviewer import review_and_link_llm_output

logger = logging.getLogger("TavusAPI")
router = APIRouter(prefix="/tavus", tags=["Tavus Video Advisor"])

TAVUS_BASE_URL = "https://tavusapi.com/v2"


class TavusSetKeyRequest(BaseModel):
    api_key: Optional[str] = None
    persona_id: Optional[str] = None
    replica_id: Optional[str] = None


class TavusCreateConversationRequest(BaseModel):
    user_role: Optional[str] = "institutional_leader"
    conversation_name: Optional[str] = None
    persona_id: Optional[str] = None
    replica_id: Optional[str] = None
    custom_greeting: Optional[str] = None
    conversational_context: Optional[str] = None
    api_key: Optional[str] = None


class TavusReviewSessionRequest(BaseModel):
    transcript_or_notes: str
    user_role: Optional[str] = "institutional_leader"
    api_key: Optional[str] = None


class TavusSyncIntelligenceRequest(BaseModel):
    query_or_transcript: str
    user_role: Optional[str] = "institutional_leader"
    conversation_id: Optional[str] = None
    api_key: Optional[str] = None


class TavusPeriodicSynthesizeRequest(BaseModel):
    recent_transcript_buffer: str
    cumulative_transcript: Optional[str] = ""
    user_role: Optional[str] = "institutional_leader"
    conversation_id: Optional[str] = None
    api_key: Optional[str] = None


def get_role_greeting(user_role: Optional[str]) -> str:
    """Returns a tailored verbal opening greeting for the video advisor based on role."""
    role = (user_role or "institutional_leader").lower()

    if role in ["institutional_leader", "provost", "vp_research"]:
        return (
            "Hello. I am Brandon Owens, your Energy Innovation Terminal Executive Advisory Partner. "
            "I'm ready to assist you in architecting your multi-year research strategy, "
            "structuring Program Opportunity Notices, and assembling regional hub consortia. "
            "What institutional initiative are we evaluating today?"
        )
    elif role in ["startup_entrepreneur", "startup", "entrepreneur", "founder"]:
        return (
            "Welcome! I am Brandon Owens, your Deep Tech Strategic Advisor at Energy Innovation Terminal. "
            "Let's look at non-dilutive capital stacking, SBIR transitions, and extending your "
            "runway while preserving your equity. What stage is your venture currently targeting?"
        )
    elif role in ["developer", "project_sponsor"]:
        return (
            "Greetings. I am Brandon Owens, your Project Finance & Demonstration Advisor. "
            "We can evaluate capital stacking, FOAK demonstration bankability, and active federal and state solicitations. "
            "Tell me about your project scope and technology readiness level."
        )
    elif role in ["investor", "vc"]:
        return (
            "Hello. I am Brandon Owens, your Climate Tech Investment Diligence Advisor. "
            "I can benchmark historical grant traction, patent moats, and co-funding multipliers from our database. "
            "Which sector or target deal would you like to review?"
        )
    elif role in ["researcher", "pi"]:
        return (
            "Hello! I am Brandon Owens, your Research Consortia & FOA Advisor. "
            "Let's examine solicitation scoring rubrics, teaming arrangements, and technology transfer pathways. "
            "Which upcoming FOA or research cluster are you preparing for?"
        )
    elif role == "utility":
        return (
            "Greetings. I am Brandon Owens, your Utility Innovation and Grid Strategy Advisor. "
            "We can discuss Non-Wires Alternatives, FERC 1920 compliance, and DERMS demonstration grants. "
            "What transmission or distribution priority are you addressing?"
        )
    elif role == "policy":
        return (
            "Hello. I am Brandon Owens, your State Energy Policy and Program Design Advisor. "
            "I'm here to help evaluate program design, statutory DAC equity targets, and intergovernmental co-funding. "
            "What policy or funding program are you shaping?"
        )
    elif role == "grant_writer":
        return (
            "Welcome. I am Brandon Owens, your Proposal & Grant Advisory Strategist. "
            "Let's review solicitation requirements, scoring rubrics, and work breakdown structures. "
            "Which grant solicitation are you preparing to write?"
        )

    return (
        "Hello! I am Brandon N. Owens, your Executive Advisor at Energy Innovation Terminal. "
        "I provide grounded strategic counsel across the US Energy Innovation Database, historical awards, and market intelligence. "
        "How can I assist you today?"
    )


def build_tavus_conversational_context(
    user_role: Optional[str],
    rag_context: Optional[str] = None,
    custom_context: Optional[str] = None
) -> str:
    """Builds a token-efficient, grounded conversational context for Tavus CVI integrating initial RAG data."""
    role_directive = get_role_prompt_directive(user_role)
    
    base_knowledge = """You are Brandon N. Owens, Senior Clean Energy Executive Advisor at Energy Innovation Terminal.
Grounded in the authoritative U.S. Energy Innovation Database by Clean Energy Research, LLC:
- 54,313 historical and active awards & grants ($98.99B USD tracked) across all 50 US states
- 5,741 funding opportunities and solicitations (NYSERDA, DOE, CEC, MassCEC, ARPA-E, NSF, EPA, Foundations, State EDAs)
- 13,948 verified recipient organizations, scale-ups, universities, national laboratories, and commercial performers
- 3,090 Principal Investigators and program contacts (100% organization linked)
- 182 USPTO Bayh-Dole clean energy patents & 173 institutional VC financings ($20.01B private capital)
- 541 award deliverables & 263 cataloged evidence vault artifacts
- 23 clean energy policies & standards (28 agency cross-links)
- 137 explorable technology subsystems across 36 frontier energy sectors

LATENCY & TOKEN OPTIMIZATION RULES:
- Be extremely rapid, direct, and concise.
- Deliver answers in 2 to 3 crisp, authoritative sentences.
- Zero filler or boilerplate intro. Speak directly to the core answer immediately.
- Ground answers precisely in verified awards, cost-share limits, and agency solicitations."""

    parts = [base_knowledge, f"ROLE STRATEGY:\n{role_directive}"]
    if rag_context:
        parts.append(f"GROUNDED DATABASE INTELLIGENCE:\n{rag_context}")
    if custom_context:
        parts.append(f"SESSION CONTEXT:\n{custom_context}")

    return "\n\n".join(parts)



@router.get("/status")
def get_tavus_status():
    """Returns the current configuration status of Tavus.io integration."""
    api_key = getattr(settings, "tavus_api_key", "") or os.environ.get("TAVUS_API_KEY", "")
    persona_id = getattr(settings, "tavus_persona_id", "") or os.environ.get("TAVUS_PERSONA_ID", "")
    replica_id = getattr(settings, "tavus_replica_id", "") or os.environ.get("TAVUS_REPLICA_ID", "")

    return {
        "tavus_configured": bool(api_key),
        "persona_id": persona_id or None,
        "replica_id": replica_id or None,
        "supported_features": [
            "realtime_video_conversation",
            "daily_webrtc_embed",
            "role_based_pal_framing",
            "dynamic_conversational_context"
        ]
    }


@router.get("/replicas")
async def get_tavus_replicas(api_key: Optional[str] = None):
    """Lists available visual replicas (faces) from Tavus account."""
    resolved_key = (
        api_key
        or getattr(settings, "tavus_api_key", "")
        or os.environ.get("TAVUS_API_KEY", "")
    )
    if not resolved_key:
        return {"data": []}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{TAVUS_BASE_URL}/replicas",
                headers={"x-api-key": resolved_key}
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                completed = [
                    {
                        "replica_id": r.get("replica_id"),
                        "replica_name": r.get("replica_name"),
                        "status": r.get("status"),
                        "thumbnail_url": r.get("thumbnail_image_url") or r.get("thumbnail_video_url")
                    }
                    for r in data if r.get("status") == "completed"
                ]
                return {"data": completed}
    except Exception as e:
        logger.warning(f"Failed to fetch Tavus replicas: {e}")
    return {"data": []}


@router.get("/personas")
async def get_tavus_personas(api_key: Optional[str] = None):
    """Lists available personas (PALs) from Tavus account."""
    resolved_key = (
        api_key
        or getattr(settings, "tavus_api_key", "")
        or os.environ.get("TAVUS_API_KEY", "")
    )
    if not resolved_key:
        return {"data": []}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{TAVUS_BASE_URL}/personas",
                headers={"x-api-key": resolved_key}
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                personas = [
                    {
                        "persona_id": p.get("persona_id"),
                        "persona_name": p.get("persona_name"),
                        "persona_description": p.get("persona_description")
                    }
                    for p in data
                ]
                return {"data": personas}
    except Exception as e:
        logger.warning(f"Failed to fetch Tavus personas: {e}")
    return {"data": []}


@router.post("/set-api-key")
async def set_tavus_api_key(req: TavusSetKeyRequest):
    """Saves and validates the Tavus API key and optional Persona/Replica IDs."""
    if req.api_key is not None:
        key = req.api_key.strip()
        if not key:
            settings.tavus_api_key = ""
            os.environ.pop("TAVUS_API_KEY", None)
        else:
            settings.tavus_api_key = key
            os.environ["TAVUS_API_KEY"] = key

    if req.persona_id is not None:
        settings.tavus_persona_id = req.persona_id.strip()
        os.environ["TAVUS_PERSONA_ID"] = req.persona_id.strip()

    if req.replica_id is not None:
        settings.tavus_replica_id = req.replica_id.strip()
        os.environ["TAVUS_REPLICA_ID"] = req.replica_id.strip()

    return {
        "success": True,
        "persona_id": settings.tavus_persona_id or None,
        "replica_id": settings.tavus_replica_id or None,
        "message": "Tavus configuration saved successfully"
    }


@router.post("/conversations/create")
async def create_tavus_conversation(
    req: TavusCreateConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Creates a new real-time video conversation session using Tavus Conversational Video Interface.
    Returns the Daily.co WebRTC room URL to embed in the frontend.
    """
    resolved_key = (
        req.api_key
        or getattr(settings, "tavus_api_key", "")
        or os.environ.get("TAVUS_API_KEY", "")
    )

    if not resolved_key:
        raise HTTPException(
            status_code=400,
            detail=(
                "Tavus API key is not configured. Please provide a Tavus API key in "
                "the video settings modal or set TAVUS_API_KEY in the environment."
            )
        )

    user_role = req.user_role or "institutional_leader"
    greeting = req.custom_greeting or get_role_greeting(user_role)

    # 1. INITIAL RAG PROCESS: Query database for top matching opportunities, awards & PIs
    rag_query = req.conversational_context or f"{user_role.replace('_', ' ')} clean energy opportunities awards funding"
    rag_data = retrieve_grounded_context(rag_query, db)

    context = build_tavus_conversational_context(
        user_role,
        rag_context=rag_data.get("context_text"),
        custom_context=req.conversational_context
    )

    persona_id = (
        req.persona_id
        or getattr(settings, "tavus_persona_id", "")
        or os.environ.get("TAVUS_PERSONA_ID", "")
        or "p8c4fc7f28ac"
    )
    replica_id = (
        req.replica_id
        or getattr(settings, "tavus_replica_id", "")
        or os.environ.get("TAVUS_REPLICA_ID", "")
        or "read903b2a48"
    )

    conversation_name = req.conversation_name or f"Energy Innovation Terminal Advisory - {user_role.replace('_', ' ').title()}"

    payload: Dict[str, Any] = {
        "conversation_name": conversation_name,
        "properties": {
            "max_call_duration": 1800,  # 30 minutes
            "participant_left_timeout": 10,  # Rapid teardown on disconnect to eliminate token burn
            "participant_absent_timeout": 60,
            "enable_recording": False,  # Save latency & encoding overhead
            "enable_transcription": True
        }
    }

    if context:
        payload["conversational_context"] = context
    if greeting:
        payload["custom_greeting"] = greeting
    if persona_id:
        payload["persona_id"] = persona_id
    if replica_id:
        payload["replica_id"] = replica_id

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            # Step 1: Clean up any stale active sessions on the account to avoid concurrency queues
            try:
                list_resp = await client.get(
                    f"{TAVUS_BASE_URL}/conversations?status=active",
                    headers={"x-api-key": resolved_key}
                )
                if list_resp.status_code == 200:
                    active_items = list_resp.json().get("data", [])
                    for act in active_items:
                        old_id = act.get("conversation_id")
                        if old_id:
                            await client.post(
                                f"{TAVUS_BASE_URL}/conversations/{old_id}/end",
                                headers={"x-api-key": resolved_key}
                            )
                            logger.info(f"Cleaned up previous active session: {old_id}")
            except Exception as e:
                logger.debug(f"Pre-call cleanup notice: {e}")

            # Step 2: Create fresh video conversation
            resp = await client.post(
                f"{TAVUS_BASE_URL}/conversations",
                headers={
                    "x-api-key": resolved_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if resp.status_code in [200, 201]:
                data = resp.json()
                logger.info(f"Successfully created Tavus conversation: {data.get('conversation_id')}")
                return {
                    "conversation_id": data.get("conversation_id"),
                    "conversation_url": data.get("conversation_url"),
                    "status": data.get("status", "active"),
                    "greeting": greeting,
                    "user_role": user_role,
                    "created_at": data.get("created_at"),
                    "citations": rag_data.get("citations", {}),
                    "context_summary": rag_data.get("context_text", "")[:400]
                }
            elif resp.status_code == 400 and ("concurrent" in resp.text.lower() or "maximum" in resp.text.lower()):
                logger.warning("Tavus returned concurrent conversation limit. Performing deep cleanup of existing sessions...")
                try:
                    list_resp = await client.get(f"{TAVUS_BASE_URL}/conversations", headers={"x-api-key": resolved_key})
                    if list_resp.status_code == 200:
                        all_items = list_resp.json().get("data", [])
                        for item in all_items:
                            if item.get("status") in ["active", "in_progress", "ready"]:
                                cid = item.get("conversation_id")
                                if cid:
                                    await client.post(f"{TAVUS_BASE_URL}/conversations/{cid}/end", headers={"x-api-key": resolved_key})
                                    logger.info(f"Terminated conflicting conversation: {cid}")
                    await asyncio.sleep(2.0)
                    # Retry creation
                    retry_resp = await client.post(
                        f"{TAVUS_BASE_URL}/conversations",
                        headers={"x-api-key": resolved_key, "Content-Type": "application/json"},
                        json=payload
                    )
                    if retry_resp.status_code in [200, 201]:
                        data = retry_resp.json()
                        logger.info(f"Successfully created Tavus conversation after auto-cleanup: {data.get('conversation_id')}")
                        return {
                            "conversation_id": data.get("conversation_id"),
                            "conversation_url": data.get("conversation_url"),
                            "status": data.get("status", "active"),
                            "greeting": greeting,
                            "user_role": user_role,
                            "created_at": data.get("created_at"),
                            "citations": rag_data.get("citations", {}),
                            "context_summary": rag_data.get("context_text", "")[:400]
                        }
                except Exception as clean_err:
                    logger.warning(f"Error during Tavus concurrent cleanup retry: {clean_err}")

                err_body = resp.text
                logger.error(f"Tavus conversation creation failed ({resp.status_code}): {err_body}")
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Tavus API error ({resp.status_code}): {err_body}"
                )
            elif resp.status_code in [504, 502, 503]:
                logger.warning(f"Tavus returned {resp.status_code}. Checking if active conversation was provisioned...")
                await asyncio.sleep(2)
                list_resp = await client.get(
                    f"{TAVUS_BASE_URL}/conversations?status=active",
                    headers={"x-api-key": resolved_key}
                )
                if list_resp.status_code == 200:
                    convs = list_resp.json().get("data", [])
                    if convs:
                        latest = convs[0]
                        if latest.get("status") == "active" and latest.get("conversation_url"):
                            logger.info(f"Recovered active conversation {latest.get('conversation_id')}")
                            return {
                                "conversation_id": latest.get("conversation_id"),
                                "conversation_url": latest.get("conversation_url"),
                                "status": "active",
                                "greeting": greeting,
                                "user_role": user_role,
                                "created_at": latest.get("created_at")
                            }
                raise HTTPException(
                    status_code=504,
                    detail="Tavus video service gateway timed out. Please try clicking Start once more."
                )
            else:
                err_body = resp.text
                logger.error(f"Tavus conversation creation failed ({resp.status_code}): {err_body}")
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Tavus API error ({resp.status_code}): {err_body}"
                )

    except (httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
        logger.warning(f"Tavus request timed out ({exc}). Checking for active conversation...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                list_resp = await client.get(
                    f"{TAVUS_BASE_URL}/conversations?status=active",
                    headers={"x-api-key": resolved_key}
                )
                if list_resp.status_code == 200:
                    convs = list_resp.json().get("data", [])
                    if convs and convs[0].get("status") == "active" and convs[0].get("conversation_url"):
                        latest = convs[0]
                        return {
                            "conversation_id": latest.get("conversation_id"),
                            "conversation_url": latest.get("conversation_url"),
                            "status": "active",
                            "greeting": greeting,
                            "user_role": user_role,
                            "created_at": latest.get("created_at")
                        }
        except Exception:
            pass
        raise HTTPException(
            status_code=504,
            detail="Tavus video room provisioning took longer than expected. Please try clicking Start once more."
        )


@router.post("/conversations/{conversation_id}/end")
async def end_tavus_conversation(
    conversation_id: str,
    api_key: Optional[str] = None
):
    """Terminates an active Tavus conversation session."""
    resolved_key = (
        api_key
        or getattr(settings, "tavus_api_key", "")
        or os.environ.get("TAVUS_API_KEY", "")
    )

    if not resolved_key:
        return {"success": True, "message": "Session ended locally"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{TAVUS_BASE_URL}/conversations/{conversation_id}/end",
                headers={"x-api-key": resolved_key}
            )
            return {"success": True, "status": resp.status_code}
    except Exception as e:
        logger.warning(f"Error ending Tavus conversation {conversation_id}: {e}")
        return {"success": True, "message": f"Ended with note: {str(e)}"}


@router.get("/conversations/{conversation_id}")
async def get_tavus_conversation_status(
    conversation_id: str,
    api_key: Optional[str] = None
):
    """Retrieves live status of a Tavus video conversation."""
    resolved_key = (
        api_key
        or getattr(settings, "tavus_api_key", "")
        or os.environ.get("TAVUS_API_KEY", "")
    )

    if not resolved_key:
        raise HTTPException(status_code=400, detail="Tavus API key required")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{TAVUS_BASE_URL}/conversations/{conversation_id}",
                headers={"x-api-key": resolved_key}
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/review-session")
def review_tavus_session(
    req: TavusReviewSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Post-LLM reference linkage back to the database.
    Scans conversation transcript, spoken dialogue, or advisory notes,
    identifies entities, awards, solicitations, and contacts, and generates
    canonical database links ([OPP:id], [ORG:id], [AWD:id], [PI:id]) and verified citations.
    """
    rag_query = req.transcript_or_notes or f"{req.user_role} clean energy"
    rag_data = retrieve_grounded_context(rag_query, db)
    reviewed = review_and_link_llm_output(req.transcript_or_notes, rag_data, db)
    return {
        "reviewed_text": reviewed["text"],
        "citations": reviewed["citations"],
        "referenced_entities": reviewed.get("referenced_entities", {})
    }


def get_technology_funding_breakdown(agency: Optional[str], db: Session, limit: int = 5) -> list:
    """Computes empirical technology funding breakdown from the historical awards database."""
    results = []
    for domain, kws in TECH_DOMAINS.items():
        conds = [Award.project_title.ilike(f"%{kw}%") for kw in kws]
        q = db.query(func.count(Award.id), func.sum(Award.award_amount))
        if agency:
            q = q.filter(Award.agency.ilike(f"%{agency}%"))
        row = q.filter(or_(*conds)).first()
        cnt = row[0] or 0
        total = float(row[1] or 0.0)
        if cnt > 0 and total > 0:
            formatted = f"${total / 1e6:.1f}M" if total >= 1e6 else f"${total / 1e3:.0f}K"
            results.append({
                "name": domain.replace("_", " ").title(),
                "domain_id": domain,
                "total_funding": total,
                "awards_count": cnt,
                "formatted_funding": formatted
            })
    results.sort(key=lambda x: x["total_funding"], reverse=True)
    return results[:limit]


@router.post("/sync-intelligence")
def sync_tavus_intelligence(
    req: TavusSyncIntelligenceRequest,
    db: Session = Depends(get_db)
):
    """
    Real-time dynamic intelligence synchronization endpoint for video advisor and chat.
    Takes live spoken questions, transcript turns, or topic keywords, executes RAG retrieval,
    extracts empirical 10-year technology breakdown, and constructs linked citations.
    """
    q_str = req.query_or_transcript.strip()
    if not q_str:
        q_str = f"{req.user_role} clean energy awards solicitations"

    intent = parse_query_intent(q_str)
    rag_data = retrieve_grounded_context(q_str, db)

    # Detect Agency Focus
    q_lower = q_str.lower()
    detected_agency = None
    if any(k in q_lower for k in ["nyserda", "new york state energy research", "nys energy"]):
        detected_agency = "NYSERDA"
    elif any(k in q_lower for k in ["nsf", "national science foundation"]):
        detected_agency = "NSF"
    elif any(k in q_lower for k in ["doe", "department of energy", "arpa-e", "eere", "oced"]):
        detected_agency = "DOE"
    elif any(k in q_lower for k in ["cec", "california energy commission"]):
        detected_agency = "CEC"
    elif any(k in q_lower for k in ["epa", "environmental protection agency"]):
        detected_agency = "EPA"
    elif any(k in q_lower for k in ["masscec", "massachusetts clean energy"]):
        detected_agency = "MassCEC"
    elif "agencies" in intent and intent["agencies"]:
        detected_agency = intent["agencies"][0]

    # Only compute tech breakdown when explicitly requested (e.g. "top funded", "ranking", "breakdown")
    tech_breakdown = []
    if any(k in q_lower for k in ["top", "highest", "ranking", "breakdown", "10 year", "funded technologies", "ledger"]):
        tech_breakdown = get_technology_funding_breakdown(detected_agency, db, limit=5)

    # Detect Topic Header
    agency_label = detected_agency or "US Energy Innovation"
    if tech_breakdown:
        detected_topic = f"{agency_label} · Top Funded Technologies"
    elif intent.get("domains"):
        domains_title = " & ".join(d.replace("_", " ").title() for d in intent["domains"][:2])
        detected_topic = f"{agency_label} · {domains_title}" if detected_agency else domains_title
    elif detected_agency:
        detected_topic = f"{agency_label} · Solicitations & Awards"
    else:
        detected_topic = f"Referenced: {q_str[:45]}"

    citations = rag_data.get("citations", {})

    total_represented_funding = sum(
        (opp.get("total_funding") or 0.0) for opp in citations.get("opportunities", [])
    ) + sum(
        (awd.get("award_amount") or 0.0) for awd in citations.get("awards", [])
    )

    return {
        "detected_topic": detected_topic,
        "active_query": q_str,
        "detected_agency": detected_agency,
        "technology_breakdown": tech_breakdown,
        "citations": citations,
        "summary": rag_data.get("context_text", "")[:400],
        "stats": {
            "total_funding": total_represented_funding,
            "awards_count": len(citations.get("awards", [])),
            "opportunities_count": len(citations.get("opportunities", [])),
            "organizations_count": len(citations.get("organizations", []))
        }
    }


@router.post("/synthesize-and-sync")
def synthesize_and_sync_tavus(
    req: TavusPeriodicSynthesizeRequest,
    db: Session = Depends(get_db)
):
    """
    Periodically (every ~30 seconds) synthesizes recent dialogue in cumulative conversation context,
    uses fast LLM to extract the core executive gist and structured search terms, and updates
    the database intelligence panel with stable, accurate opportunities and awards.
    """
    recent_text = req.recent_transcript_buffer.strip()
    cumulative_text = (req.cumulative_transcript or "").strip() or recent_text

    if not recent_text and not cumulative_text:
        return {
            "executive_gist": "Awaiting conversation...",
            "detected_topic": "Live Discussion Focus",
            "search_query": "",
            "key_entities": [],
            "citations": {"opportunities": [], "awards": [], "organizations": [], "contacts": []},
            "stats": {"total_funding": 0.0, "awards_count": 0, "opportunities_count": 0, "organizations_count": 0}
        }

    resolved_api_key = req.api_key or getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    executive_gist = ""
    detected_topic = ""
    search_query = ""
    key_entities = []

    if resolved_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=resolved_api_key)
            prompt = f"""You are the intelligence engine for the Energy Innovation Terminal.
Analyze the following conversation dialogue between a clean energy user and an AI advisor:

RECENT 30-SECOND DIALOGUE:
\"\"\"{recent_text}\"\"\"

CUMULATIVE CONVERSATION HISTORY:
\"\"\"{cumulative_text[-2500:]}\"\"\"

TASK:
1. Summarize the executive gist of what is currently being evaluated in 1 crisp, authoritative sentence.
2. Identify a concise, professional topic focus title (e.g. 'NSF & SBIR Thermal Battery Grants' or 'Building Decarbonization Heat Pump Incentives').
3. Construct the ideal 3 to 6 keyword search query to retrieve the most relevant funding solicitations (PONs/FOAs), historical awards, and research institutions from the database.
4. Extract key entities mentioned (agencies like NYSERDA, NSF, DOE, EPA; programs; universities; technologies).

Respond ONLY with valid JSON in this exact structure:
{{
  "executive_gist": "...",
  "detected_topic": "...",
  "search_query": "...",
  "key_entities": ["..."]
}}"""

            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=350,
            )
            data = json.loads(completion.choices[0].message.content or "{}")
            executive_gist = data.get("executive_gist", "")
            detected_topic = data.get("detected_topic", "")
            search_query = data.get("search_query", "")
            key_entities = data.get("key_entities", [])
        except Exception as e:
            logger.warning(f"OpenAI 30s synthesis note: {e}")

    # Fallback heuristic if LLM did not run or returned empty
    if not search_query:
        search_query = f"{recent_text} {cumulative_text[-300:]}"
    if not executive_gist:
        executive_gist = f"Grounded intelligence for {search_query[:75]}..."
    if not detected_topic:
        detected_topic = "Live Discussion Focus"

    # Query the Grounded Database with the synthesized search query
    rag_data = retrieve_grounded_context(search_query, db)
    citations = rag_data.get("citations", {})

    total_represented_funding = sum(
        (opp.get("total_funding") or 0.0) for opp in citations.get("opportunities", [])
    ) + sum(
        (awd.get("award_amount") or 0.0) for awd in citations.get("awards", [])
    )

    return {
        "executive_gist": executive_gist,
        "detected_topic": detected_topic,
        "search_query": search_query,
        "key_entities": key_entities,
        "citations": citations,
        "summary": rag_data.get("context_text", "")[:400],
        "stats": {
            "total_funding": total_represented_funding,
            "awards_count": len(citations.get("awards", [])),
            "opportunities_count": len(citations.get("opportunities", [])),
            "organizations_count": len(citations.get("organizations", []))
        }
    }

