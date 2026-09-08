"""
Post-LLM Reviewer and Entity Reference Insertion Engine.
Performs deterministic scanning of LLM output to:
1. Detect unlinked mentions of solicitations, organizations, awards, and PIs.
2. Insert canonical [OPP:id], [ORG:id], [AWD:id], [PI:id] and markdown links.
3. Validate all citation IDs against authoritative PostgreSQL database records.
4. Append/structure verified database cross-references.
"""


import re
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.models.opportunity import Opportunity
from app.models.recipient import Recipient
from app.models.award import Award
from app.models.contact import Contact

logger = logging.getLogger("PostLLMReviewer")

SOLICITATION_REGEX = re.compile(
    r'\b(?:PON|FOA|DE-FOA|GFO|RFA|RFP|SOL|NOFO)[\s\-:]*([A-Za-z0-9\-_]{2,16})\b',
    re.IGNORECASE
)

# Common clean energy agency acronyms
KNOWN_AGENCIES = {"NYSERDA", "CEC", "MassCEC", "DOE", "ARPA-E", "NSF", "EPA", "NJEDA", "OCED", "MESC", "EERE"}

def review_and_link_llm_output(
    raw_text: str,
    rag_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Executes a comprehensive post-LLM review pass:
    - Injects entity links for unbracketed mentions
    - Validates existing [OPP:id], [ORG:id], [AWD:id], [PI:id] markers
    - Assembles verified references dictionary with rich database metadata
    """
    if not raw_text:
        return {"text": "", "citations": rag_data.get("citations", {}), "referenced_entities": {}}

    citations = rag_data.get("citations", {})
    retrieved_opps = {str(o["id"]): o for o in citations.get("opportunities", [])}
    retrieved_orgs = {str(r["id"]): r for r in citations.get("organizations", [])}
    retrieved_awds = {str(a["id"]): a for a in citations.get("awards", [])}
    retrieved_pis = {str(p["id"]): p for p in citations.get("contacts", [])}

    text = raw_text
    referenced_opp_ids: Set[int] = set()
    referenced_org_ids: Set[int] = set()
    referenced_awd_ids: Set[int] = set()
    referenced_pi_ids: Set[int] = set()

    # 1. Collect and validate existing bracketed citations [OPP:id], [ORG:id], etc.
    def validate_opp_match(match):
        cid = match.group(1)
        if cid in retrieved_opps:
            referenced_opp_ids.add(int(cid))
            return f"[OPP:{cid}]"
        # Check DB
        opp = db.query(Opportunity).filter(Opportunity.id == int(cid)).first() if cid.isdigit() else None
        if opp:
            referenced_opp_ids.add(opp.id)
            if str(opp.id) not in retrieved_opps:
                retrieved_opps[str(opp.id)] = _format_opp_dict(opp)
            return f"[OPP:{opp.id}]"
        return match.group(0)

    text = re.sub(r'\[OPP:(\d+)\]', validate_opp_match, text)

    def validate_org_match(match):
        cid = match.group(1)
        if cid in retrieved_orgs:
            referenced_org_ids.add(int(cid))
            return f"[ORG:{cid}]"
        org = db.query(Recipient).filter(Recipient.id == int(cid)).first() if cid.isdigit() else None
        if org:
            referenced_org_ids.add(org.id)
            if str(org.id) not in retrieved_orgs:
                retrieved_orgs[str(org.id)] = _format_org_dict(org)
            return f"[ORG:{org.id}]"
        return match.group(0)

    text = re.sub(r'\[ORG:(\d+)\]', validate_org_match, text)

    def validate_awd_match(match):
        cid = match.group(1)
        if cid in retrieved_awds:
            referenced_awd_ids.add(int(cid))
            return f"[AWD:{cid}]"
        awd = db.query(Award).filter(Award.id == int(cid)).first() if cid.isdigit() else None
        if awd:
            referenced_awd_ids.add(awd.id)
            if str(awd.id) not in retrieved_awds:
                retrieved_awds[str(awd.id)] = _format_awd_dict(awd)
            return f"[AWD:{awd.id}]"
        return match.group(0)

    text = re.sub(r'\[AWD:(\d+)\]', validate_awd_match, text)

    def validate_pi_match(match):
        cid = match.group(1)
        if cid in retrieved_pis:
            referenced_pi_ids.add(int(cid))
            return f"[PI:{cid}]"
        ct = db.query(Contact).filter(Contact.id == int(cid)).first() if cid.isdigit() else None
        if ct:
            referenced_pi_ids.add(ct.id)
            if str(ct.id) not in retrieved_pis:
                retrieved_pis[str(ct.id)] = _format_pi_dict(ct)
            return f"[PI:{ct.id}]"
        return match.group(0)

    text = re.sub(r'\[PI:(\d+)\]', validate_pi_match, text)

    # 2. Link unbracketed Opportunities by Solicitation Number
    # Example: "under PON 5650" -> "under PON 5650 [OPP:123]" or "[PON 5650](/opportunities/123)"
    for opp_id_str, opp_data in retrieved_opps.items():
        sol_num = opp_data.get("solicitation_number")
        if sol_num and len(sol_num) >= 3:
            pattern = re.compile(r'\b(' + re.escape(sol_num) + r')(?!\s*\[OPP:)\b', re.IGNORECASE)
            if pattern.search(text):
                referenced_opp_ids.add(int(opp_id_str))
                text = pattern.sub(rf'\1 [OPP:{opp_id_str}]', text)

    # Scan for other solicitation numbers mentioned in text that were not in initial RAG
    for match in SOLICITATION_REGEX.finditer(text):
        num = match.group(1)
        if len(num) >= 3 and not any(f"[OPP:{oid}]" in text for oid in referenced_opp_ids):
            opp = db.query(Opportunity).filter(
                Opportunity.solicitation_number.ilike(f"%{num}%")
            ).first()
            if opp:
                referenced_opp_ids.add(opp.id)
                retrieved_opps[str(opp.id)] = _format_opp_dict(opp)
                # Replace mention with citation
                pattern = re.compile(r'\b(' + re.escape(match.group(0)) + r')(?!\s*\[OPP:)\b', re.IGNORECASE)
                text = pattern.sub(rf'\1 [OPP:{opp.id}]', text, count=1)

    # 3. Link unbracketed Organizations / Recipients from RAG & DB
    for org_id_str, org_data in retrieved_orgs.items():
        org_name = org_data.get("name")
        if org_name and len(org_name) >= 5 and org_name.lower() not in {"general electric", "department of energy"}:
            # Check if name appears without [ORG:
            pattern = re.compile(r'\b(' + re.escape(org_name) + r')(?!\s*\[ORG:)\b', re.IGNORECASE)
            if pattern.search(text):
                referenced_org_ids.add(int(org_id_str))
                text = pattern.sub(rf'\1 [ORG:{org_id_str}]', text, count=1)

    # 4. Link unbracketed Principal Investigators from RAG
    for pi_id_str, pi_data in retrieved_pis.items():
        pi_name = pi_data.get("name")
        if pi_name and len(pi_name) >= 6:
            pattern = re.compile(r'\b(' + re.escape(pi_name) + r')(?!\s*\[PI:)\b', re.IGNORECASE)
            if pattern.search(text):
                referenced_pi_ids.add(int(pi_id_str))
                text = pattern.sub(rf'\1 [PI:{pi_id_str}]', text, count=1)

    # 5. Clean up any accidental double brackets or trailing asterisks
    text = text.replace("**", "").strip()

    # 6. Build final structured citations payload containing ONLY verified referenced entities + top context
    verified_citations = {
        "opportunities": list(retrieved_opps.values()),
        "organizations": list(retrieved_orgs.values()),
        "awards": list(retrieved_awds.values()),
        "contacts": list(retrieved_pis.values()),
        "technologies": citations.get("technologies", []),
        "macro_impacts": citations.get("macro_impacts", {}),
        "referenced_ids": {
            "opportunities": list(referenced_opp_ids),
            "organizations": list(referenced_org_ids),
            "awards": list(referenced_awd_ids),
            "contacts": list(referenced_pi_ids),
        },
        "statistics": {
            "retrieved_opportunities_count": len(retrieved_opps),
            "retrieved_awards_count": len(retrieved_awds),
            "retrieved_organizations_count": len(retrieved_orgs),
            "retrieved_contacts_count": len(retrieved_pis),
            "actively_cited_count": len(referenced_opp_ids) + len(referenced_org_ids) + len(referenced_awd_ids) + len(referenced_pi_ids)
        }
    }

    return {
        "text": text,
        "citations": verified_citations,
        "actively_cited": verified_citations["statistics"]["actively_cited_count"]
    }


def _format_opp_dict(opp: Opportunity) -> Dict[str, Any]:
    return {
        "citation_id": f"OPP:{opp.id}",
        "id": opp.id,
        "solicitation_number": opp.solicitation_number,
        "name": opp.name,
        "agency": opp.agency,
        "status": opp.status,
        "total_funding": opp.total_funding,
        "max_per_award": opp.max_per_award,
        "cost_share_pct": opp.cost_share_pct,
        "due_date": opp.due_date_display,
        "short_description": opp.short_description,
        "url": f"/opportunities/{opp.id}"
    }

def _format_org_dict(rec: Recipient) -> Dict[str, Any]:
    return {
        "citation_id": f"ORG:{rec.id}",
        "id": rec.id,
        "name": rec.name,
        "recipient_type": rec.recipient_type,
        "city": rec.headquarters_city,
        "state": rec.headquarters_state,
        "sector": rec.sector,
        "primary_technology": rec.primary_technology,
        "total_funding": rec.total_funding_received,
        "awards_count": rec.total_awards_count,
        "stage": rec.commercialization_stage,
        "url": "/organizations"
    }

def _format_awd_dict(awd: Award) -> Dict[str, Any]:
    return {
        "citation_id": f"AWD:{awd.id}",
        "id": awd.id,
        "project_title": awd.project_title,
        "recipient_name": awd.recipient_name,
        "award_amount": awd.award_amount,
        "agency": awd.agency,
        "year": awd.year,
        "state": awd.recipient_state,
        "pi_name": awd.pi_name,
        "project_abstract": (awd.project_abstract or "").strip()[:140],
        "url": "/awards"
    }

def _format_pi_dict(ct: Contact) -> Dict[str, Any]:
    return {
        "citation_id": f"PI:{ct.id}",
        "id": ct.id,
        "name": ct.name_display,
        "title": ct.title,
        "institution": ct.institution_name,
        "email": ct.email,
        "state": ct.state,
        "awards_count": ct.awards_count,
        "total_funding": ct.total_funding,
        "url": "/contacts"
    }
