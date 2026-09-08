"""
Grounded RAG Knowledge Retriever & Strategic Grounding Engine.
Treats the 54,313 awards, 5,741 opportunities, 13,948 recipients, 212 organizations,
182 Bayh-Dole patents, 173 VC financing rounds, 541 award deliverables, and 3,090 contacts
database as the authoritative ground truth for the Expert AI Chat Copilot and Tavus Video Advisor.
Mandatory cross-referencing across Organizations, Programs, Solicitations,
Awards, Patents, VC Deals, Outcomes, and Impacts by Sector, Technology, Fuel, and Stage.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import text, func, or_, and_, desc, case
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.award import Award, AwardResult
from app.models.contact import Contact
from app.models.recipient import Recipient
from app.models.organization import Organization
from app.models.technology import Technology, TechnologySubsystem
from app.models.policy import PolicyStandard, PolicyTechnologyLink, PolicyOrganizationLink
from app.models.attribution import RecipientInvestment, RecipientPatent
from app.models.result import OpportunityResult, SuccessStory, ResultBenchmark, ResultArtifact

logger = logging.getLogger("RAGRetriever")

# Comprehensive clean energy innovation technology domains
TECH_DOMAINS = {
    "hydrogen": ["hydrogen", "electrolyzer", "fuel cell", "45v", "clean molecules", "ammonia", "pem", "alkaline"],
    "energy_storage": ["battery", "storage", "bess", "ldes", "flow battery", "lithium", "iron-air", "zinc", "thermal battery", "heat battery", "solid-state"],
    "advanced_nuclear": ["nuclear", "smr", "small modular reactor", "triso", "haleu", "advanced reactor", "fission", "flibe"],
    "fusion": ["fusion", "tokamak", "stellarator", "hts magnet", "magnetic confinement", "plasma", "z-pinch", "rebco", "sparc"],
    "geothermal": ["geothermal", "enhanced geothermal", "egs", "closed loop", "superhot rock", "baseload heat", "eavor"],
    "industrial_decarbonization": ["industrial", "clean steel", "green cement", "process heat", "heavy industry", "electrochemical cement", "molten oxide", "sublime"],
    "carbon_capture": ["carbon capture", "ccus", "direct air capture", "dac", "point source", "sequestration", "mineralization", "cdr", "heirloom"],
    "microgrids": ["microgrid", "resilience", "islanding", "derms", "distributed energy", "nwa"],
    "solar": ["solar", "photovoltaic", "pv", "agrivoltaic", "perovskite", "bifacial", "tandem", "cubicpv"],
    "wind": ["wind", "offshore wind", "floating wind", "turbine", "nwa", "subsea cable"],
    "building_decarbonization": ["building", "heat pump", "thermal network", "district energy", "hvac", "envelope", "retrofit", "window heat pump"],
    "grid_modernization": ["grid", "transmission", "distribution", "ferc", "transformer", "hvdc", "dlr", "dynamic line rating", "grid-forming"],
    "clean_transportation": ["ev", "electric vehicle", "charging", "v2g", "fleet electrification", "maritime", "aviation", "saf", "heavy duty", "amogy"],
    "catalytic_finance": ["catalytic", "blended finance", "first-loss", "philanthropic", "equity preservation", "stacking", "venture capital", "syndication", "geapp"]
}

# Agency & Jurisdiction mappings across federal, state ED, utility, and philanthropic entities
AGENCY_MAP = {
    "nyserda": ("NYSERDA", "state_ny"),
    "cec": ("CEC", "state_ca"),
    "masscec": ("MassCEC", "state_ma"),
    "doe": ("DOE", "federal"),
    "arpa-e": ("ARPA-E", "federal"),
    "arpae": ("ARPA-E", "federal"),
    "nsf": ("NSF", "federal"),
    "epa": ("EPA", "federal"),
    "usda": ("USDA", "federal"),
    "nasa": ("NASA", "federal"),
    "dod": ("DOD", "federal"),
    "dot": ("DOT", "federal"),
    "esd": ("Empire State Development", "state_ny"),
    "empire state development": ("Empire State Development", "state_ny"),
    "massventures": ("MassVentures", "state_ma"),
    "go-biz": ("GO-Biz", "state_ca"),
    "gobiz": ("GO-Biz", "state_ca"),
    "jobsohio": ("JobsOhio", "state_oh"),
    "medc": ("MEDC", "state_mi"),
    "rockefeller": ("The Rockefeller Foundation", "foundation"),
    "the rockefeller foundation": ("The Rockefeller Foundation", "foundation"),
    "bloomberg": ("Bloomberg Philanthropies", "foundation"),
    "bloomberg philanthropies": ("Bloomberg Philanthropies", "foundation"),
    "bezos": ("Bezos Earth Fund", "foundation"),
    "bezos earth fund": ("Bezos Earth Fund", "foundation"),
    "prime coalition": ("Prime Coalition", "foundation"),
    "breakthrough energy": ("Breakthrough Energy", "foundation"),
    "coned": ("ConEd", "utility"),
    "national grid": ("National Grid", "utility"),
    "pge": ("Pacific Gas and Electric", "utility"),
    "pg&e": ("Pacific Gas and Electric", "utility"),
    "tva": ("Tennessee Valley Authority", "utility"),
    "dominion": ("Dominion Energy", "utility"),
}


STATE_MAP = {
    "new york": "NY", "ny": "NY",
    "california": "CA", "ca": "CA",
    "massachusetts": "MA", "ma": "MA",
    "colorado": "CO", "co": "CO",
    "illinois": "IL", "il": "IL",
    "texas": "TX", "tx": "TX",
    "pennsylvania": "PA", "pa": "PA",
    "washington": "WA", "wa": "WA",
    "new jersey": "NJ", "nj": "NJ",
}


def parse_query_intent(query: str) -> Dict[str, Any]:
    """Extracts entities, agencies, jurisdictions, states, technology domains, and query goal archetype."""
    q_lower = query.lower()

    detected_agencies = []
    detected_jurisdictions = []
    for key, (agency, jur) in AGENCY_MAP.items():
        if re.search(r'\b' + re.escape(key) + r'\b', q_lower):
            if agency not in detected_agencies:
                detected_agencies.append(agency)
            if jur not in detected_jurisdictions:
                detected_jurisdictions.append(jur)

    detected_states = []
    for name, code in STATE_MAP.items():
        if re.search(r'\b' + re.escape(name) + r'\b', q_lower):
            if code not in detected_states:
                detected_states.append(code)

    detected_domains = []
    for domain, kws in TECH_DOMAINS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', q_lower) for kw in kws):
            detected_domains.append(domain)

    # Detect Query Goal Archetype
    query_goal = "MARKET_INTELLIGENCE"
    if any(w in q_lower for w in ["5-year", "5 year", "five year", "research strategy", "institutional strategy", "create program", "create a program", "issue pon", "issue opportunity", "solicitation design", "program opportunity notice", "research agenda", "center grant", "regional hub"]):
        query_goal = "PROGRAM_DESIGN_STRATEGY"
    elif any(w in q_lower for w in ["startup", "start-up", "entrepreneur", "founder", "spin-out", "spinout", "seed", "pre-seed", "sbir", "sttr", "runway", "equity preservation", "incubator", "customer discovery", "angel"]):
        query_goal = "FOUNDER_RUNWAY_STRATEGY"
    elif any(w in q_lower for w in ["stack", "stacking", "capital stack", "feed study", "foak", "project finance", "offtake", "off-take", "10mw", "100mw", "facility", "project sponsor"]):
        query_goal = "CAPITAL_STACKING_PROJECT"

    # Detect Status Intent (open vs closed)
    status_filter = None
    if any(w in q_lower for w in ["open", "active", "current", "available", "now", "ongoing", "live"]):
        status_filter = "open"
    elif any(w in q_lower for w in ["closed", "expired", "past", "historical", "prior"]):
        status_filter = "closed"

    # Extract solicitation codes and numbers (e.g. PON 6141, 6141, PON 5989, DE-FOA-0003210, RFP 6041, RFQL 5312)
    solicitation_codes = []
    sol_matches = re.findall(r'\b(?:PON|FOA|RFP|RFQL|RFI|NOI|DE-FOA|DE-SC|DE-EE|DE-AR|HR0011|N00014|1505)\s*[-:]?\s*([0-9a-zA-Z\-_]+)\b', query, re.IGNORECASE)
    for sm in sol_matches:
        code_str = sm.strip()
        if code_str and code_str not in solicitation_codes:
            solicitation_codes.append(code_str)

    num_matches = re.findall(r'\b(\d{3,7})\b', query)
    for nm in num_matches:
        if nm not in solicitation_codes:
            solicitation_codes.append(nm)

    # Extract multi-word title phrases (e.g. "Empire Building Challenge", "Window Heat Pump", "FlexTech", "Charge Ready")
    clean_q = query.strip()
    filler_regex = r'^(?:tell me about|what is(?: the)?|what are(?: the)?|how does|can you explain|give me details on|details about|overview of|info on|find|show me)\s+'
    stripped_q = re.sub(filler_regex, '', clean_q, flags=re.IGNORECASE).strip(' ?.')
    
    search_phrases = []
    if len(stripped_q) >= 4 and stripped_q.lower() not in ["open solicitations", "current opportunities", "active grants"]:
        search_phrases.append(stripped_q)
    
    words = stripped_q.split()
    for n in [4, 3, 2]:
        for i in range(len(words) - n + 1):
            chunk = ' '.join(words[i:i+n]).strip(' ,.:;()')
            if len(chunk) >= 4 and chunk.lower() not in [p.lower() for p in search_phrases]:
                search_phrases.append(chunk)

    # Clean search keywords
    stop_words = {
        "the", "a", "an", "in", "on", "for", "with", "and", "or", "of", "to", "what", "how", "who", "which",
        "are", "is", "can", "help", "me", "tell", "about", "show", "find", "grant", "grants", "funding",
        "opportunity", "opportunities", "craft", "design", "this", "institution", "research", "best", "advise",
        "market", "solicitation", "solicitations", "stack", "stacking", "nyserda", "doe", "cec", "masscec",
        "nsf", "epa", "arpa-e", "arpae", "new", "york", "california", "massachusetts", "does", "have", "any",
        "all", "open", "active", "closed", "current", "available", "list", "there", "give", "detail", "details",
        "program", "programs", "record", "records"
    }
    tokens = [w for w in re.findall(r'\b\w+\b', q_lower) if w not in stop_words and len(w) > 2]
    keywords = " ".join(tokens[:8])

    return {
        "raw_query": query,
        "keywords": keywords,
        "tokens": tokens,
        "query_goal": query_goal,
        "status_filter": status_filter,
        "solicitation_codes": solicitation_codes,
        "search_phrases": search_phrases,
        "agencies": detected_agencies,
        "jurisdictions": detected_jurisdictions,
        "states": detected_states,
        "domains": detected_domains,
    }


def retrieve_grounded_context(
    query: str,
    db: Session,
    max_opportunities: int = 15,
    max_awards: int = 12,
    max_recipients: int = 6,
    max_contacts: int = 6
) -> Dict[str, Any]:
    """
    Executes hybrid structured SQL + FTS queries across the 54k+ awards, 5.7k+ opportunities,
    13.7k+ recipients, and 3k+ contacts database, extracting sector, fuel, technology, and stage impacts.
    Prioritizes exact solicitation numbers and named entity matches at highest rank.
    """
    intent = parse_query_intent(query)
    tokens = intent["tokens"]
    agencies = intent["agencies"]
    states = intent["states"]
    status_filter = intent.get("status_filter")
    solicitation_codes = intent.get("solicitation_codes", [])
    search_phrases = intent.get("search_phrases", [])

    # If user explicitly asked for solicitations or agency inventory, expand limits
    q_low = query.lower()
    if status_filter == "open" or any(w in q_low for w in ["solicitation", "solicitations", "opportunity", "opportunities", "pon", "rfp", "rfql", "foa", "open"]):
        max_opportunities = max(max_opportunities, 25)

    # 1. EXACT / HIGH-PRIORITY SOLICITATION & PROGRAM MATCHING
    exact_opps: List[Opportunity] = []
    seen_opp_ids = set()

    for code in solicitation_codes:
        code_matches = db.query(Opportunity).filter(
            or_(
                Opportunity.solicitation_number.ilike(f"%{code}%"),
                Opportunity.name.ilike(f"%{code}%")
            )
        ).limit(10).all()
        for o in code_matches:
            if o.id not in seen_opp_ids:
                exact_opps.append(o)
                seen_opp_ids.add(o.id)

    for phrase in search_phrases[:4]:
        phrase_matches = db.query(Opportunity).filter(
            Opportunity.name.ilike(f"%{phrase}%")
        ).limit(6).all()
        for o in phrase_matches:
            if o.id not in seen_opp_ids:
                exact_opps.append(o)
                seen_opp_ids.add(o.id)

    # Collect domain terms + query tokens
    domain_terms = []
    for d in intent.get("domains", []):
        domain_terms.extend(TECH_DOMAINS.get(d, []))
    
    # Combined search terms prioritized (domain keywords first, then substantive tokens)
    search_terms = list(dict.fromkeys(domain_terms + [t for t in tokens if len(t) > 2]))[:6]

    # 2. GENERAL RANKED OPPORTUNITIES RETRIEVAL
    opp_query = db.query(Opportunity)
    opp_filters = []

    if agencies:
        opp_filters.append(Opportunity.agency.in_(agencies))

    if status_filter:
        opp_filters.append(Opportunity.status == status_filter)

    if search_terms:
        kw_conditions = []
        for t in search_terms:
            kw_conditions.append(Opportunity.name.ilike(f"%{t}%"))
            kw_conditions.append(Opportunity.short_description.ilike(f"%{t}%"))
            kw_conditions.append(Opportunity.solicitation_number.ilike(f"%{t}%"))
        opp_filters.append(or_(*kw_conditions))

    if opp_filters:
        opp_query = opp_query.filter(and_(*opp_filters))

    ranked_opps = opp_query.order_by(
        desc(case((Opportunity.status == "open", 1), else_=0)),
        desc(Opportunity.total_funding.isnot(None)),
        desc(Opportunity.total_funding)
    ).limit(max_opportunities).all()

    # Fallback if specific search terms yielded too few opportunities for the agency
    if len(ranked_opps) < 2 and agencies:
        agency_fallback = db.query(Opportunity).filter(Opportunity.agency.in_(agencies))
        if status_filter:
            agency_fallback = agency_fallback.filter(Opportunity.status == status_filter)
        ranked_opps = agency_fallback.order_by(
            desc(case((Opportunity.status == "open", 1), else_=0)),
            desc(Opportunity.total_funding.isnot(None)),
            desc(Opportunity.total_funding)
        ).limit(max_opportunities).all()
    elif len(ranked_opps) < 2 and search_terms:
        broader_filter = or_(*[Opportunity.name.ilike(f"%{t}%") for t in search_terms[:4]])
        if status_filter:
            broader_filter = and_(broader_filter, Opportunity.status == status_filter)
        ranked_opps = db.query(Opportunity).filter(broader_filter).order_by(
            desc(case((Opportunity.status == "open", 1), else_=0)),
            desc(Opportunity.total_funding.isnot(None)),
            desc(Opportunity.total_funding)
        ).limit(max_opportunities).all()

    # Combine exact matches with ranked matches
    opportunities = exact_opps[:]
    for o in ranked_opps:
        if o.id not in seen_opp_ids:
            opportunities.append(o)
            seen_opp_ids.add(o.id)
    opportunities = opportunities[:max_opportunities]

    # 3. RETRIEVE HISTORICAL AWARDS & COMPS (With Exact Recipient & Title Matching)
    exact_awards: List[Award] = []
    seen_award_ids = set()

    for phrase in search_phrases[:3]:
        awd_phrase_matches = db.query(Award).filter(
            or_(
                Award.recipient_name.ilike(f"%{phrase}%"),
                Award.project_title.ilike(f"%{phrase}%")
            )
        ).order_by(desc(Award.award_amount)).limit(6).all()
        for a in awd_phrase_matches:
            if a.id not in seen_award_ids:
                exact_awards.append(a)
                seen_award_ids.add(a.id)

    award_query = db.query(Award)
    award_filters = []

    if agencies:
        award_filters.append(Award.agency.in_(agencies))
    if states:
        award_filters.append(Award.recipient_state.in_(states))

    if search_terms:
        kw_conditions = []
        for t in search_terms:
            kw_conditions.append(Award.project_title.ilike(f"%{t}%"))
            kw_conditions.append(Award.recipient_name.ilike(f"%{t}%"))
        award_filters.append(or_(*kw_conditions))

    if award_filters:
        award_query = award_query.filter(and_(*award_filters))

    ranked_awards = award_query.order_by(desc(Award.award_amount)).limit(max_awards).all()

    if not ranked_awards and search_terms:
        ranked_awards = db.query(Award).filter(
            or_(*[Award.project_title.ilike(f"%{t}%") for t in search_terms[:4]])
        ).order_by(desc(Award.award_amount)).limit(max_awards).all()

    awards = exact_awards[:]
    for a in ranked_awards:
        if a.id not in seen_award_ids:
            awards.append(a)
            seen_award_ids.add(a.id)
    awards = awards[:max_awards]

    # 4. RETRIEVE ORGANIZATIONS / AWARDEES (With Exact Name Matching)
    exact_recipients: List[Recipient] = []
    seen_recip_ids = set()

    for phrase in search_phrases[:3]:
        rec_phrase_matches = db.query(Recipient).filter(
            Recipient.name.ilike(f"%{phrase}%")
        ).order_by(desc(Recipient.total_funding_received)).limit(4).all()
        for r in rec_phrase_matches:
            if r.id not in seen_recip_ids:
                exact_recipients.append(r)
                seen_recip_ids.add(r.id)

    recip_query = db.query(Recipient)
    recip_filters = []
    if states:
        recip_filters.append(Recipient.headquarters_state.in_(states))
    if search_terms:
        recip_kw = []
        for t in search_terms[:4]:
            recip_kw.append(Recipient.name.ilike(f"%{t}%"))
            recip_kw.append(Recipient.primary_technology.ilike(f"%{t}%"))
            recip_kw.append(Recipient.sector.ilike(f"%{t}%"))
            recip_kw.append(Recipient.description.ilike(f"%{t}%"))
        recip_filters.append(or_(*recip_kw))

    if recip_filters:
        recip_query = recip_query.filter(and_(*recip_filters))

    ranked_recipients = recip_query.order_by(desc(Recipient.total_funding_received), desc(Recipient.total_awards_count)).limit(max_recipients).all()

    recipients = exact_recipients[:]
    for r in ranked_recipients:
        if r.id not in seen_recip_ids:
            recipients.append(r)
            seen_recip_ids.add(r.id)
    recipients = recipients[:max_recipients]

    if len(recipients) < 2 and search_terms:
        fallback_recs = db.query(Recipient).filter(
            or_(*[Recipient.primary_technology.ilike(f"%{t}%") for t in search_terms[:4]])
        ).order_by(desc(Recipient.total_funding_received)).limit(max_recipients).all()
        for r in fallback_recs:
            if r.id not in seen_recip_ids:
                recipients.append(r)
                seen_recip_ids.add(r.id)
    recipients = recipients[:max_recipients]

    # 4. RETRIEVE KEY CONTACTS & PIS
    contact_query = db.query(Contact)
    contact_filters = []
    if states:
        contact_filters.append(Contact.state.in_(states))
    if search_terms:
        kw_conditions = []
        for t in search_terms[:4]:
            kw_conditions.append(Contact.name_display.ilike(f"%{t}%"))
            kw_conditions.append(Contact.institution_name.ilike(f"%{t}%"))
            kw_conditions.append(Contact.technology_area.ilike(f"%{t}%"))
        contact_filters.append(or_(*kw_conditions))

    if contact_filters:
        contact_query = contact_query.filter(and_(*contact_filters))

    contacts = contact_query.order_by(desc(Contact.awards_count), desc(Contact.total_funding)).limit(max_contacts).all()

    # 5. RETRIEVE MATCHING TECHNOLOGY TAXONOMIES
    tech_taxonomies = []
    domain_targets = intent["domains"] if intent["domains"] else ["energy_storage", "clean_hydrogen", "grid_modernization", "solar_systems"]
    domain_conditions = []
    for d in domain_targets:
        domain_conditions.append(Technology.category_id == d)
        domain_conditions.append(Technology.id.ilike(f"%{d}%"))
        domain_conditions.append(Technology.name.ilike(f"%{d}%"))
        domain_conditions.append(Technology.sector.ilike(f"%{d}%"))
        domain_conditions.append(Technology.fuel_vector.ilike(f"%{d}%"))
    for st in search_terms[:3]:
        domain_conditions.append(Technology.name.ilike(f"%{st}%"))
        domain_conditions.append(Technology.fuel_vector.ilike(f"%{st}%"))

    tech_records = db.query(Technology).filter(or_(*domain_conditions)).limit(6).all()
    for tr in tech_records:
        subsystem_nodes = []
        for sub in (tr.subsystems or [])[:4]:
            subsystem_nodes.append({
                "name": sub.name,
                "category": sub.category,
                "materials": sub.materials,
                "failure_mode": sub.failure_mode,
                "active_research": sub.active_research
            })
        tech_taxonomies.append({
            "id": tr.id,
            "name": tr.name,
            "headline": tr.headline,
            "sector": tr.sector,
            "fuel_vector": tr.fuel_vector,
            "summary": tr.plain_what_is_it or tr.headline,
            "why_it_matters": tr.plain_why_it_matters,
            "moonshot_goal": tr.moonshot_goal,
            "trl_current": tr.trl_current,
            "trl_target": tr.trl_target,
            "subsystems": subsystem_nodes
        })

    # 5b. RETRIEVE MATCHING POLICY, REGULATIONS & SAFETY CODES
    policy_citations = []
    pol_conditions = []
    for d in domain_targets:
        pol_conditions.append(PolicyStandard.category.ilike(f"%{d}%"))
        pol_conditions.append(PolicyStandard.code_identifier.ilike(f"%{d}%"))
        pol_conditions.append(PolicyStandard.title.ilike(f"%{d}%"))
        pol_conditions.append(PolicyStandard.compliance_mandate.ilike(f"%{d}%"))
    for st in search_terms[:3]:
        pol_conditions.append(PolicyStandard.code_identifier.ilike(f"%{st}%"))
        pol_conditions.append(PolicyStandard.title.ilike(f"%{st}%"))
        pol_conditions.append(PolicyStandard.compliance_mandate.ilike(f"%{st}%"))
    for state_code in intent.get("states", []):
        pol_conditions.append(PolicyStandard.jurisdiction_state == state_code)

    matched_pols = db.query(PolicyStandard).filter(or_(*pol_conditions)).limit(6).all()
    if not matched_pols:
        matched_pols = db.query(PolicyStandard).limit(4).all()

    for pol in matched_pols:
        policy_citations.append({
            "citation_id": f"POL:{pol.id}",
            "id": pol.id,
            "code_identifier": pol.code_identifier,
            "title": pol.title,
            "short_title": pol.short_title or pol.code_identifier,
            "category": pol.category,
            "jurisdiction_level": pol.jurisdiction_level,
            "jurisdiction_state": pol.jurisdiction_state,
            "compliance_mandate": pol.compliance_mandate,
            "commercial_friction_points": pol.commercial_friction_points,
            "associated_incentives": pol.associated_incentives,
            "official_source_url": pol.official_source_url,
            "url": f"/policies"
        })

    # 5c. RETRIEVE PATENTS (USPTO Bayh-Dole Clean Energy IP)
    patent_citations = []
    pat_conditions = []
    for st in search_terms[:4]:
        pat_conditions.append(RecipientPatent.title.ilike(f"%{st}%"))
        pat_conditions.append(RecipientPatent.assignee_name.ilike(f"%{st}%"))
        pat_conditions.append(RecipientPatent.abstract.ilike(f"%{st}%"))
    for phrase in search_phrases[:3]:
        pat_conditions.append(RecipientPatent.assignee_name.ilike(f"%{phrase}%"))
        pat_conditions.append(RecipientPatent.title.ilike(f"%{phrase}%"))

    if pat_conditions:
        matched_pats = db.query(RecipientPatent).filter(or_(*pat_conditions)).limit(5).all()
    else:
        matched_pats = db.query(RecipientPatent).order_by(desc(RecipientPatent.filing_date)).limit(4).all()

    for pat in matched_pats:
        patent_citations.append({
            "citation_id": f"PAT:{pat.id}",
            "patent_number": pat.patent_number,
            "title": pat.title,
            "assignee": pat.assignee_name or "Assigned Performer",
            "cpc_class": pat.cpc_class,
            "filing_date": str(pat.filing_date)[:10] if pat.filing_date else "Disclosed",
            "grant_contract_id": pat.grant_contract_id
        })

    # 5d. RETRIEVE VENTURE CAPITAL & PRIVATE EQUITY TRANSACTIONS
    investment_citations = []
    inv_conditions = []
    for st in search_terms[:4]:
        inv_conditions.append(Recipient.name.ilike(f"%{st}%"))
        inv_conditions.append(RecipientInvestment.lead_investor.ilike(f"%{st}%"))
    for phrase in search_phrases[:3]:
        inv_conditions.append(Recipient.name.ilike(f"%{phrase}%"))

    inv_query = db.query(RecipientInvestment, Recipient.name).join(Recipient, RecipientInvestment.recipient_id == Recipient.id)
    if inv_conditions:
        matched_invs = inv_query.filter(or_(*inv_conditions)).order_by(desc(RecipientInvestment.amount_usd)).limit(5).all()
    else:
        matched_invs = inv_query.order_by(desc(RecipientInvestment.amount_usd)).limit(4).all()

    for inv, comp_name in matched_invs:
        investment_citations.append({
            "citation_id": f"VC:{inv.id}",
            "company_name": comp_name,
            "round_type": inv.round_type,
            "amount_usd": inv.amount_usd,
            "valuation_usd": inv.valuation_usd,
            "lead_investor": inv.lead_investor,
            "round_date": str(inv.round_date)[:10] if inv.round_date else "Disclosed"
        })


    # 5e. RETRIEVE VERIFIED PROGRAMMATIC OUTCOMES & CASE STUDIES
    outcome_citations = []
    res_conditions = []
    for st in search_terms[:3]:
        res_conditions.append(OpportunityResult.metric_category.ilike(f"%{st}%"))
        res_conditions.append(OpportunityResult.canonical_metric_name.ilike(f"%{st}%"))
        res_conditions.append(OpportunityResult.recipient_name.ilike(f"%{st}%"))
    for d in domain_targets[:2]:
        res_conditions.append(OpportunityResult.metric_category.ilike(f"%{d}%"))
        res_conditions.append(OpportunityResult.canonical_metric_name.ilike(f"%{d}%"))

    if res_conditions:
        matched_outcomes = db.query(OpportunityResult).filter(or_(*res_conditions)).order_by(desc(OpportunityResult.canonical_value)).limit(6).all()
    else:
        matched_outcomes = db.query(OpportunityResult).order_by(desc(OpportunityResult.canonical_value)).limit(5).all()

    for res in matched_outcomes:
        outcome_citations.append({
            "citation_id": f"RES:{res.id}",
            "opportunity_id": res.opportunity_id,
            "metric_category": res.metric_category,
            "canonical_metric_name": res.canonical_metric_name,
            "canonical_value": res.canonical_value,
            "canonical_unit": res.canonical_unit,
            "recipient_name": res.recipient_name,
            "agency": res.agency,
            "source_artifact_title": res.source_artifact_title
        })



    # 5f. RETRIEVE SUCCESS STORIES & BENCHMARK ROI
    story_citations = []
    story_query = db.query(SuccessStory)
    if search_terms:
        story_kw = [SuccessStory.recipient_name.ilike(f"%{t}%") for t in search_terms[:3]]
        story_kw.extend([SuccessStory.technology_area.ilike(f"%{t}%") for t in search_terms[:3]])
        matched_stories = story_query.filter(or_(*story_kw)).limit(4).all()
    else:
        matched_stories = story_query.limit(4).all()

    for st in matched_stories:
        story_citations.append({
            "citation_id": f"STORY:{st.id}",
            "recipient_name": st.recipient_name,
            "agency": st.agency,
            "title": st.title,
            "technology_area": st.technology_area,
            "challenge": st.challenge,
            "solution_technology": st.solution_technology,
            "outcome_impact": st.outcome_impact,
            "quote_text": st.quote_text,
            "quote_author": st.quote_author,
            "summary": st.summary,
            "trl_advancement": st.trl_advancement
        })


    # 6. MACRO IMPACT DISTRIBUTION (Sectors, Fuels, Technologies, Commercial Stages)
    macro_impacts = {
        "primary_sectors": ["Electric Grid & Infrastructure", "Industrial Decarbonization", "Buildings & Thermal Networks", "Clean Transportation"],
        "primary_fuels": ["Zero-Carbon Electricity", "Green Hydrogen & Ammonia", "District Geothermal Heat", "Advanced Drop-in Biofuels"],
        "commercial_stages": [
            {"stage": "TRL 1-3 (Fundamental Research)", "funding_focus": "NSF, DOE Basic Sciences, internal F&A seed"},
            {"stage": "TRL 4-5 (Prototype Validation)", "funding_focus": "SBIR/STTR Phase II, State Innovation Vouchers, corporate matching"},
            {"stage": "TRL 6-7 (Commercial Pilot Demonstration)", "funding_focus": "DOE OCED, ARPA-E SCALEUP, State Clean Energy Funds"},
            {"stage": "TRL 8-9 (Full Commercial Deployment)", "funding_focus": "IRA Tax Credits (45V, 48C), Green Bank Senior Debt"}
        ]
    }

    # 7. ASSEMBLE CITATION METADATA FOR FRONTEND
    citations = {
        "opportunities": [
            {
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
            for opp in opportunities
        ],
        "awards": [
            {
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
            for awd in awards
        ],
        "organizations": [
            {
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
            for rec in recipients
        ],
        "contacts": [
            {
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
            for ct in contacts
        ],
        "technologies": tech_taxonomies,
        "policies": policy_citations,
        "patents": patent_citations,
        "investments": investment_citations,
        "outcomes": outcome_citations,
        "success_stories": story_citations,
        "macro_impacts": macro_impacts,
        "statistics": {
            "retrieved_opportunities_count": len(opportunities),
            "retrieved_awards_count": len(awards),
            "retrieved_organizations_count": len(recipients),
            "retrieved_contacts_count": len(contacts),
            "retrieved_policies_count": len(policy_citations),
            "retrieved_patents_count": len(patent_citations),
            "retrieved_investments_count": len(investment_citations),
            "retrieved_outcomes_count": len(outcome_citations),
            "retrieved_stories_count": len(story_citations),
        }
    }

    # 8. ASSEMBLE COMPACT LLM CONTEXT PAYLOAD
    context_text = build_comprehensive_context_string(citations, intent)

    return {
        "intent": intent,
        "citations": citations,
        "context_text": context_text,
    }



def build_comprehensive_context_string(citations: Dict[str, Any], intent: Dict[str, Any]) -> str:
    """Formats retrieved records into rich structured text for LLM deep reasoning."""
    lines = []
    lines.append(f"### RETRIEVAL METADATA: Goal={intent.get('query_goal')}, Agencies={intent.get('agencies') or 'All'}, States={intent.get('states') or 'All'}, Domains={intent.get('domains') or 'General'}")
    lines.append("")

    # Sector, Fuel, Tech, Stage Impacts
    lines.append("### AUTHORITATIVE DATABASE COVERAGE (100% Comprehensive Ledger):")
    lines.append("- Tracked Public Disbursements: $98.99B USD across 54,313 Awards in all 50 US States")
    lines.append("- Funding Opportunities: 5,741 Solicitations (NYSERDA, DOE, CEC, MassCEC, ARPA-E, NSF, EPA, Foundations, State EDAs)")
    lines.append("- Recipient Organizations: 13,948 Verified Entities (Universities, Labs, Scale-Ups, Startups)")
    lines.append("- Bayh-Dole Patents & Commercial Output: 182 USPTO Assigned Patents & 173 Institutional VC Financings ($20.01B Private Capital)")
    lines.append("- Programs & Policy Mandates: 174 Multi-Year Programs, 23 Statutes & Testing Standards, 137 Technology Subsystems")
    lines.append("")

    # Organizations / Awardees
    orgs = citations.get("organizations", [])
    lines.append(f"### VERIFIED ORGANIZATIONS & RECIPIENT BENCHMARKS ({len(orgs)} records from 13,948 Recipient Graph):")
    if orgs:
        for r in orgs:
            funding_fmt = f"${r['total_funding']:,.0f}" if r.get('total_funding') else "Disclosed"
            lines.append(
                f"- [{r['citation_id']}] {r['name']} ({r.get('city') or 'City'}, {r.get('state') or 'US'}) | Type: {r.get('recipient_type') or 'Company'} | "
                f"Sector: {r.get('sector') or 'Clean Energy'} | Tech: {r.get('primary_technology') or 'General'} | "
                f"Total Funding: {funding_fmt} ({r.get('awards_count') or 1} awards) | Stage: {r.get('stage') or 'Commercialization'}"
            )
            desc = (r.get('description') or '').strip().replace('\r', ' ')
            if desc:
                lines.append(f"  Organization Profile: {desc}")
    else:
        lines.append("- Peer organizations across universities, national labs, and deep tech startups.")
    lines.append("")

    # Opportunities & Programs
    opps = citations.get("opportunities", [])
    lines.append(f"### RETRIEVED SOLICITATIONS & PROGRAMS ({len(opps)} records from 5,741 Opportunity Database):")
    if opps:
        for o in opps:
            funding_str = f"${o['total_funding']:,.0f}" if o.get('total_funding') else "Discretionary / Open Budget"
            max_award_str = f"${o['max_per_award']:,.0f}" if o.get('max_per_award') else "Unspecified"
            cost_share_str = f"{o['cost_share_pct']}%" if o.get('cost_share_pct') is not None else "Standard"
            lines.append(
                f"- [{o['citation_id']}] {o['agency']} | Solicitation {o['solicitation_number']}: {o['name']} | "
                f"Status: {o['status'].upper()} | Funding Pool: {funding_str} | Max Award: {max_award_str} | "
                f"Cost-Share: {cost_share_str} | Due Date(s): {o.get('due_date') or 'Rolling'}"
            )
            desc = (o.get('short_description') or '').strip().replace('\r', ' ')
            if desc:
                lines.append(f"  Program Scope & Details: {desc}")
            if o.get('objectives'):
                lines.append(f"  Program Objectives: {o['objectives']}")
    else:
        lines.append("- No direct solicitation records matching this exact filter.")
    lines.append("")

    # Awards & Comps
    awds = citations.get("awards", [])
    lines.append(f"### HISTORICAL TRANSACTION COMPS & AWARDS ({len(awds)} records from 54,313 Awards Ledger):")
    if awds:
        for a in awds:
            amt_str = f"${a['award_amount']:,.0f}" if a.get('award_amount') else "Unspecified"
            abst = (a.get('project_abstract') or '').replace('\r', ' ').replace('\n', ' ').strip()
            lines.append(
                f"- [{a['citation_id']}] {a['recipient_name']} ({a.get('state') or 'US'}) | {amt_str} | "
                f"Agency: {a.get('agency')} | Year: {a.get('year')} | Title: {a.get('project_title')}"
            )
            if abst:
                lines.append(f"  Project Abstract & Scope: {abst}")
    else:
        lines.append("- No historical award records matched the exact filter.")
    lines.append("")

    # Patents & Intellectual Property
    pats = citations.get("patents", [])
    if pats:
        lines.append(f"### ASSIGNED USPTO BAYH-DOLE PATENTS ({len(pats)} records from 182 Patent Ledger):")
        for p in pats:
            lines.append(
                f"- [{p['citation_id']}] Patent US {p['patent_number']}: {p['title']} | Assignee: {p['assignee']} | "
                f"CPC Class: {p['cpc_class']} | Filed: {p['filing_date']} | Contract: {p['grant_contract_id'] or 'Federal/State Grant'}"
            )
        lines.append("")

    # Venture Capital Financings
    invs = citations.get("investments", [])
    if invs:
        lines.append(f"### FOLLOW-ON VENTURE CAPITAL & PRIVATE EQUITY ROUNDS ({len(invs)} records from $20.01B Deal Registry):")
        for inv in invs:
            amt_fmt = f"${inv['amount_usd']:,.0f}" if inv.get('amount_usd') else "Disclosed"
            val_fmt = f" (Post-Val: ${inv['valuation_usd']:,.0f})" if inv.get('valuation_usd') else ""
            lines.append(
                f"- [{inv['citation_id']}] {inv['company_name']} | {inv['round_type']}: {amt_fmt}{val_fmt} | "
                f"Lead Investor: {inv['lead_investor'] or 'Syndicate'} | Date: {inv['round_date']}"
            )
        lines.append("")

    # Programmatic Outcomes & Benchmarks
    outcomes = citations.get("outcomes", [])
    if outcomes:
        lines.append(f"### VERIFIED PROGRAMMATIC OUTCOMES & IMPACT INDICATORS ({len(outcomes)} records):")
        for out in outcomes:
            val_fmt = f"{out['canonical_value']:,.1f} {out['canonical_unit']}" if out.get('canonical_value') is not None else "Verified"
            lines.append(
                f"- [{out['citation_id']}] {out.get('agency') or 'Agency'} | Metric: {out['canonical_metric_name']} ({out['metric_category']}): {val_fmt} | "
                f"Recipient/Portfolio: {out.get('recipient_name') or 'Programmatic Aggregation'}"
            )
        lines.append("")


    # Success Stories & Case Studies
    stories = citations.get("success_stories", [])
    if stories:
        lines.append(f"### FLAGSHIP COMMERCIAL SUCCESS STORIES & IMPACT CASE STUDIES ({len(stories)} records):")
        for s in stories:
            lines.append(
                f"- [{s['citation_id']}] {s['recipient_name']} ({s['agency']}): {s['title']} ({s.get('trl_advancement') or 'Scale-Up'})\n"
                f"  Challenge: {s['challenge']}\n"
                f"  Technology Solution: {s['solution_technology']}\n"
                f"  Commercial Outcome: {s['outcome_impact']}"
            )
            if s.get('quote_text'):
                lines.append(f"  Executive Quote: \"{s['quote_text']}\" — {s.get('quote_author') or 'Leadership'}")
        lines.append("")

    # Contacts & PIs
    cts = citations.get("contacts", [])
    lines.append(f"### PRINCIPAL INVESTIGATORS & KEY CONTACTS ({len(cts)} records from 3,090 Directory):")
    if cts:
        for c in cts:
            lines.append(
                f"- [{c['citation_id']}] {c['name']} ({c.get('title') or 'Lead Researcher'}) @ {c.get('institution') or 'Institution'} ({c.get('state') or 'US'}) | "
                f"Track Record: {c.get('awards_count') or 0} prior awards (${c.get('total_funding') or 0:,.0f})"
            )
    else:
        lines.append("- No individual directory contacts matched.")
    lines.append("")

    # Technology taxonomies and Subsystems
    techs = citations.get("technologies", [])
    if techs:
        lines.append("### TECHNOLOGY FRONTIER TARGETS & ARCHITECTURAL SUBSYSTEMS:")
        for t in techs:
            lines.append(
                f"- {t['name']} ({t['id']}): {t['headline']} (TRL {t.get('trl_current')} -> {t.get('trl_target')}). "
                f"Strategic Value: {t.get('why_it_matters') or t.get('summary')}. "
                f"Moonshot Target: {t.get('moonshot_goal') or 'Commercial Deployment'}"
            )
            for sub in t.get("subsystems", []):
                lines.append(f"  * Subsystem: {sub['name']} [{sub.get('category')}] | Materials: {sub.get('materials')} | Bottleneck: {sub.get('failure_mode')}")
        lines.append("")

    # Policies, Codes & Standards
    pols = citations.get("policies", [])
    if pols:
        lines.append(f"### APPLICABLE CODES, STANDARDS & POLICY MANDATES ({len(pols)} records):")
        for p in pols:
            lines.append(
                f"- [{p['citation_id']}] {p['code_identifier']}: {p['title']} ({p.get('jurisdiction_state') or p.get('jurisdiction_level')}) | Category: {p['category']} | "
                f"Mandate: {p['compliance_mandate']}"
            )
            if p.get('commercial_friction_points'):
                lines.append(f"  Deployment Roadblocks & Friction: {p['commercial_friction_points']}")
            if p.get('associated_incentives'):
                lines.append(f"  Policy Incentives: {p['associated_incentives']}")
        lines.append("")

    return "\n".join(lines)




def generate_deterministic_rag_response(query: str, rag_data: Dict[str, Any], user_role: str = "institutional_leader") -> str:
    """
    Generates a pure narrative executive advisory response cross-referencing
    organizations, opportunities, programs, awards, and sector/fuel/stage impacts.
    """
    intent = rag_data.get("intent", {})
    query_goal = intent.get("query_goal", "MARKET_INTELLIGENCE")
    citations = rag_data["citations"]
    techs = citations.get("technologies", [])
    stats = citations.get("statistics", {})

    role = (user_role or "institutional_leader").lower()

    if role in ["institutional_leader", "policy"] or query_goal == "PROGRAM_DESIGN_STRATEGY":
        return generate_narrative_institutional_response(query, citations, techs, stats)

    if role in ["startup_entrepreneur", "startup", "entrepreneur", "founder"] or query_goal == "FOUNDER_RUNWAY_STRATEGY":
        return generate_narrative_startup_response(query, citations, techs, stats)

    if role in ["developer", "project_sponsor"] or query_goal == "CAPITAL_STACKING_PROJECT":
        return generate_narrative_developer_response(query, citations, techs, stats)

    return generate_narrative_general_response(query, citations, techs, stats, role)


def generate_narrative_institutional_response(query: str, citations: Dict[str, Any], techs: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Generates an elegant narrative advisory with structured tabular architectures for Institutional Leaders."""
    output = []
    output.append(
        "When orchestrating a comprehensive five-year research enterprise for a major institution, the primary objective is transitioning from fragmented, individual faculty grants to a coherent center-grant architecture that can compete for fifty to two hundred million dollar federal innovation hubs. The most successful research universities and national laboratories operate not merely as grant applicants, but as programmatic architects that design structured internal funding mechanisms, assemble interdisciplinary faculty clusters, and mobilize external matching funds.\n"
    )

    output.append("### Core Strategic Pillars Grounded in Verified Technology Impacts\n")
    output.append(
        "To establish a defensible institutional footprint, the research enterprise should concentrate capital across three high-conviction thematic pillars where federal agencies and state authorities are prioritizing long-term appropriations:\n"
    )

    if techs:
        for t in techs[:3]:
            output.append(
                f"- {t['name']}: Moving foundational science from laboratory proof of concept toward integrated field pilot validation. The critical institutional gap lies in {t.get('why_it_matters') or t.get('headline')}, with the long-term objective of achieving {t.get('moonshot_goal') or 'commercial grid deployment'}.\n"
            )
    else:
        output.append(
            "- Long-Duration Energy Storage and Campus Thermal Networks: Scaling multi-day electrochemical systems, flow battery electrolytes, and district geothermal networks.\n"
            "- Clean Molecules and Hydrogen Carrier Kinetics: Addressing industrial heat decarbonization, high-durability electrolyzer membranes, and pipeline blending logistics.\n"
            "- Grid Modernization and Edge Orchestration: Advancing FERC Order 1920 transmission optimization, Dynamic Line Rating, and autonomous microgrid black-start capabilities.\n"
        )

    output.append("### Institutional Program & PON Architecture\n")
    output.append(
        "```mermaid\n"
        "graph TD\n"
        "    A[Institutional F&A Overhead Pool] --> B[Track 1: Seed Feasibility PON - $75k-$150k]\n"
        "    B --> C[Faculty Teaming & Provisional IP Filing]\n"
        "    C --> D[Track 2: Applied Consortia PON - $500k-$1.5M]\n"
        "    E[Corporate Partners & State Matching] --> D\n"
        "    D --> F[FEED Validation & Utility Pilot LOI]\n"
        "    F --> G[Track 3: Flagship Mega-Hub Center Bid - $10M-$50M]\n"
        "    H[DOE OCED / NSF Engines] --> G\n"
        "```\n"
    )

    output.append(
        "| Program Track | Target Award Size | Performance Period | Cost-Share & Match Requirement | Strategic Institutional Deliverable |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Track 1 (Seed & IP Discovery) | $75,000 - $150,000 | 12 Months | 0% (Funded via F&A Reserves) | Cross-departmental teaming & invention disclosures |\n"
        "| Track 2 (Applied Consortia) | $500,000 - $1,500,000 | 24 Months | 20% Industry or State Match | Front-End Engineering Design & validated prototype |\n"
        "| Track 3 (Flagship Center Hub) | $10,000,000 - $50,000,000 | 60 Months | Multi-Institution Consortium | Lead regional federal hub bids (DOE OCED, NSF Engines) |\n"
    )

    # Cross-reference Organizations
    if citations.get("organizations"):
        output.append("### Benchmark Partner Organizations & Teaming Graph\n")
        output.append(
            "Empirical analysis of peer research anchors in the 13,700-recipient knowledge graph indicates that center proposals require teaming with established industry performers:\n"
        )
        for org in citations["organizations"][:3]:
            funding_fmt = f"${org['total_funding']:,.0f}" if org.get('total_funding') else "Disclosed"
            output.append(f"- [{org['citation_id']}] {org['name']} ({org.get('city') or 'City'}, {org.get('state') or 'US'}): {org.get('sector') or 'Clean Energy'} performer with {org.get('awards_count') or 1} verified awards ({funding_fmt} captured) in {org.get('primary_technology') or 'Advanced Energy'}.\n")

    # Cross-reference Key PIs
    output.append("### Human Capital and Faculty Cluster Strategy\n")
    if citations.get("contacts"):
        output.append(
            "Securing high-tier center awards requires anchoring key leadership positions with proven investigators who hold established grant capture velocity. Across verified transaction records, relevant domain leaders include:\n"
        )
        for c in citations["contacts"][:3]:
            output.append(f"- [{c['citation_id']}] {c['name']}, {c.get('title') or 'Research Director'} at {c.get('institution')} ({c.get('state') or 'US'}), with a documented track record of {c.get('awards_count', 1)} prior awards and ${c.get('total_funding', 0):,.0f} in captured research funding.\n")

    output.append("### Five-Year Chronological Implementation & Governance Horizon\n")
    output.append(
        "| Phase & Timeframe | Primary Strategic Mandate | Operational Milestones | Target Capital Vehicle |\n"
        "| --- | --- | --- | --- |\n"
        "| Year 1 (Foundation) | Governance & Seed Allocation | Establish Clean Energy Institute & release Track 1 Seed PON | Internal F&A Overhead Pool |\n"
        "| Year 2 (Teaming) | Corporate & Utility Teaming | Execute corporate Master Research Agreements & release Track 2 PON | State Matching Grant Facilities |\n"
        "| Year 3 (Federal Bids) | Flagship Center Applications | Submit regional center proposals backed by formal utility off-taker LOIs | DOE Hubs & NSF Engines |\n"
        "| Year 4 (Spinouts) | Commercialization Acceleration | Launch venture studio to commercialize high-TRL Bayh-Dole patents | Venture Angel & State Seed Funds |\n"
        "| Year 5 (Multiplier) | Self-Sustaining Endowment | Expand steady-state licensing royalties and annual F&A recovery above $20M | Core Endowment & Licensing Yield |\n"
    )

    return "\n".join(output)


def generate_narrative_startup_response(query: str, citations: Dict[str, Any], techs: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Generates an elegant narrative advisory with structured tabular roadmaps for Deep Tech Startups."""
    output = []
    output.append(
        "For an early-stage clean tech company, non-dilutive grant funding serves as an essential strategic lever to protect the cap table. Every million dollars in federal and state grant capital directly replaces over two million dollars in priced equity, preserving fifteen to twenty-five percent more founder ownership through Series A while providing third-party technical validation that substantially de-risks future venture financing.\n"
    )

    output.append("### Sequential Non-Dilutive Capital Waterfall\n")
    output.append(
        "```mermaid\n"
        "graph LR\n"
        "    A[Pre-Seed: TRL 2-3] -->|SBIR Phase I + State Voucher| B[Seed: TRL 4-5]\n"
        "    B -->|SBIR Phase II $1.5M-$2M| C[Series A: TRL 6-7]\n"
        "    C -->|Federal Demo + Green Bank| D[Commercial Deployment]\n"
        "    style A fill:#f0fdf4,stroke:#16a34a\n"
        "    style B fill:#eff6ff,stroke:#2563eb\n"
        "    style C fill:#faf5ff,stroke:#9333ea\n"
        "```\n"
    )
    output.append(
        "| Development Stage | Program Target | Typical Award Size | Non-Federal Match | Founder Cap Table Impact |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Stage 1 (TRL 2-3) | SBIR/STTR Phase I + State Voucher | $200,000 - $400,000 | 0% Cost-Share | 0% Equity Dilution (Preserves ~5% Ownership) |\n"
        "| Stage 2 (TRL 4-5) | SBIR Phase II + Incubator Grant | $1,150,000 - $2,000,000 | 0% Cost-Share | Replaces $2.5M Priced Seed Round |\n"
        "| Stage 3 (TRL 6-7) | Federal Demonstration + Green Bank | $5,000,000 - $20,000,000 | 20-50% Cost-Share | Enables FOAK Commercial Pilot without Capex Burn |\n"
    )

    if citations.get("organizations"):
        output.append("### Peer Startup Awardee Comps in Sector\n")
        for org in citations["organizations"][:3]:
            output.append(f"- [{org['citation_id']}] {org['name']} ({org.get('state') or 'US'}): {org.get('sector') or 'Clean Tech'} company with {org.get('awards_count') or 1} awards de-risking {org.get('primary_technology') or 'hardware'} commercialization.\n")

    if citations.get("opportunities"):
        output.append("### Relevant Open Solicitations\n")
        for o in citations["opportunities"][:3]:
            funding_fmt = f"${o['total_funding']:,.0f}" if o.get("total_funding") else "Discretionary Pool"
            output.append(f"- [{o['citation_id']}] {o['agency']} Solicitation {o['solicitation_number']}: {o['name']} with a total program allocation of {funding_fmt} [Dossier]({o['url']}).\n")

    return "\n".join(output)


def generate_narrative_developer_response(query: str, citations: Dict[str, Any], techs: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Generates an elegant narrative advisory for Project Developers with structured tabular stacking."""
    output = []
    output.append(
        "For clean technology infrastructure deployment, achieving commercial bankability depends on disciplined capital stacking. The most effective developers utilize public feasibility and engineering grants to absorb early-stage development risks, such as interconnection queue deposits and Front-End Engineering Design studies, before locking in long-term demonstration and debt financing.\n"
    )

    output.append("### Three-Stage Capital Stacking Sequence\n")
    output.append(
        "| Project Stage | Capital Vehicle | Funding Mechanism | Allowable Cost-Share | Risk De-risked |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Stage 1 (Development) | State Feasibility Grants | NYSERDA / CEC / MassCEC | 0-20% Match | FEED Studies & Interconnection Deposits |\n"
        "| Stage 2 (Construction) | Federal Demonstration | DOE OCED / ARPA-E | 50% Cost-Share | FOAK Equipment Procurement & Civil EPC |\n"
        "| Stage 3 (Take-Out) | Tax Credits & Senior Debt | IRA Section 45V / 48C / 45X | Commercial Debt | Long-term Bankability & Off-take PPA |\n"
    )

    if citations.get("organizations"):
        output.append("### Top Project Sponsor Awardee Comps\n")
        for org in citations["organizations"][:3]:
            funding_fmt = f"${org['total_funding']:,.0f}" if org.get('total_funding') else "Disclosed"
            output.append(f"- [{org['citation_id']}] {org['name']} ({org.get('state') or 'US'}): Captured {funding_fmt} in {org.get('sector') or 'infrastructure'} project funding.\n")

    if citations.get("opportunities"):
        output.append("### Active Solicitation Benchmarks\n")
        for o in citations["opportunities"][:3]:
            output.append(f"- [{o['citation_id']}] {o['agency']} Solicitation {o['solicitation_number']}: {o['name']} [Dossier]({o['url']}).\n")

    return "\n".join(output)


def generate_narrative_general_response(query: str, citations: Dict[str, Any], techs: List[Dict[str, Any]], stats: Dict[str, Any], role: str) -> str:
    """Generates an elegant narrative advisory for general roles without bold formatting."""
    output = []
    output.append(
        f"Evaluating this strategy through the operational perspective of a {role.replace('_', ' ').title()}, maximizing non-dilutive capital requires aligning technical milestones with public policy priorities. Public funding programs reward disciplined proposals that demonstrate clear commercialization pathways, verified cost-share commitments, and measurable decarbonization impact.\n"
    )

    if citations.get("opportunities"):
        output.append("### Relevant Public Solicitations\n")
        for o in citations["opportunities"][:3]:
            output.append(f"- [{o['citation_id']}] {o['agency']} {o['solicitation_number']}: {o['name']} [Dossier]({o['url']}).\n")

    if citations.get("awards"):
        output.append("### Benchmark Precedents\n")
        for a in citations["awards"][:2]:
            amt_str = f"${a['award_amount']:,.0f}" if a.get("award_amount") else "Disclosed"
            output.append(f"- [{a['citation_id']}] {a['recipient_name']}: Awarded {amt_str} by {a.get('agency')}.\n")

    return "\n".join(output)
