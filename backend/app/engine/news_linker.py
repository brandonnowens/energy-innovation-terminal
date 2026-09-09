"""
High-Precision Energy Innovation Relevance Filter, Entity Resolution & LLM Summarizer Engine.
Strictly links incoming clean energy news explicitly to specific database elements:
- Opportunities (PONs, FOAs, RFPs) -> /opportunities?id=...
- Organizations (Funders, Utilities, Companies) -> /organizations?org=...
- Programs (Funding Initiatives) -> /programs?search=...
- Awards & Awardees (Grants Ledger, Startups, Labs) -> /awards?search=...
- Technologies (Taxonomy & Subsystems) -> /technologies?tech=...
- Policies & Regulatory Proceedings (NFPA 855, FERC Order 1920, IRA 45V) -> /dockets?search=...
"""

import re
import hashlib
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func

from app.config import settings

logger = logging.getLogger("NewsLinker")

# Domain Keywords for Sector Categorization
ENERGY_INNOVATION_TAXONOMY = {
    "Long-Duration Energy Storage": [
        "long-duration energy storage", "ldes", "iron-air", "flow battery", "vanadium redox",
        "thermal energy storage", "compressed air energy storage", "caes", "gravity storage",
        "zinc-air", "sodium-ion", "form energy", "eos energy", "liquid metal battery", "iron-flow"
    ],
    "Grid Modernization & Transmission": [
        "grid modernization", "transmission", "ferc order 1920", "ferc order 2023", "interconnection",
        "derms", "virtual power plant", "vpp", "non-wires alternative", "nwa", "microgrid",
        "hosting capacity", "smart inverter", "grid-forming inverter", "dynamic line rating", "synchrophasor"
    ],
    "Clean Hydrogen & Derivatives": [
        "clean hydrogen", "green hydrogen", "electrolyzer", "pem electrolyzer", "solid oxide electrolyzer",
        "soec", "hydrogen hub", "45v", "clean ammonia", "sustainable aviation fuel", "saf", "e-fuel", "hydrogen turbine"
    ],
    "Advanced Nuclear & SMR": [
        "advanced nuclear", "small modular reactor", "smr", "microreactor", "fusion energy",
        "tokamak", "stellarator", "commonwealth fusion", "x-energy", "kairos power", "terrapower", "nuscale"
    ],
    "Building Decarbonization & Thermal": [
        "building decarbonization", "thermal energy network", "district heating", "heat pump",
        "cold-climate heat pump", "local law 97", "ashrae 90.1", "embodied carbon", "induction heating",
        "smart thermostat", "refrigerant transition", "r-454b", "geothermal district"
    ],
    "Offshore Wind & Marine Energy": [
        "offshore wind", "floating offshore wind", "floating foundation", "oswt", "subsea cable",
        "masscec wind", "nyserda offshore wind", "blade recycling", "tidal energy", "wave energy"
    ],
    "Industrial Heat & CCUS": [
        "industrial decarbonization", "direct air capture", "dac", "carbon capture", "point-source capture",
        "thermal battery", "green cement", "green steel", "co2 mineralization", "industrial heat pump"
    ],
    "Advanced Solar & PV": [
        "perovskite", "tandem solar", "bifacial pv", "agrivoltaics", "floating solar", "floatovoltaics",
        "pv recycling", "cadmium telluride", "topcon", "heterojunction"
    ],
    "Clean Transportation & Heavy EV": [
        "heavy-duty ev", "megawatt charging", "mcs", "fleet electrification", "electric bus",
        "v2g", "vehicle-to-grid", "solid-state battery", "battery recycling", "lithium-sulfur"
    ],
    "Federal & State Capital Grants": [
        "funding opportunity announcement", "foa", "program opportunity notice", "pon",
        "arpa-e award", "doe grant", "nyserda funding", "cec gfo", "masscec grant", "sbir phase ii",
        "title 17 loan", "lpo loan", "bipartisan infrastructure law", "inflation reduction act"
    ]
}

KNOWN_ORGANIZATIONS = [
    {"name": "NYSERDA", "aliases": ["nyserda", "new york state energy research and development authority"], "org_type": "State Authority", "path": "/organizations?org=NYSERDA"},
    {"name": "U.S. Department of Energy (DOE)", "aliases": ["doe", "department of energy", "energy.gov"], "org_type": "Federal Agency", "path": "/organizations?org=U.S. Department of Energy (DOE)"},
    {"name": "ARPA-E", "aliases": ["arpa-e", "advanced research projects agency-energy"], "org_type": "Federal Agency", "path": "/organizations?org=ARPA-E"},
    {"name": "California Energy Commission (CEC)", "aliases": ["california energy commission", "cec"], "org_type": "State Authority", "path": "/organizations?org=California Energy Commission (CEC)"},
    {"name": "MassCEC", "aliases": ["massachusetts clean energy center", "masscec"], "org_type": "State Authority", "path": "/organizations?org=MassCEC"},
    {"name": "National Renewable Energy Laboratory (NREL)", "aliases": ["nrel", "national renewable energy laboratory"], "org_type": "National Laboratory", "path": "/organizations?org=National Renewable Energy Laboratory (NREL)"},
    {"name": "FERC", "aliases": ["federal energy regulatory commission", "ferc"], "org_type": "Federal Regulator", "path": "/organizations?org=FERC"},
    {"name": "Consolidated Edison (ConEd)", "aliases": ["coned", "con edison", "consolidated edison"], "org_type": "Electric Utility", "path": "/organizations?org=Consolidated Edison (ConEd)"},
    {"name": "National Grid", "aliases": ["national grid", "natgrid"], "org_type": "Electric Utility", "path": "/organizations?org=National Grid"},
    {"name": "New York Power Authority (NYPA)", "aliases": ["nypa", "new york power authority"], "org_type": "Public Power Utility", "path": "/organizations?org=New York Power Authority (NYPA)"},
    {"name": "Long Island Power Authority (LIPA)", "aliases": ["lipa", "long island power authority"], "org_type": "Public Power Utility", "path": "/organizations?org=Long Island Power Authority (LIPA)"},
    {"name": "Form Energy", "aliases": ["form energy"], "org_type": "Clean Tech Startup", "path": "/awards?search=Form%20Energy"},
    {"name": "Eos Energy Enterprises", "aliases": ["eos energy", "eos energy enterprises"], "org_type": "Clean Tech Company", "path": "/awards?search=Eos%20Energy"},
    {"name": "Bloom Energy", "aliases": ["bloom energy"], "org_type": "Clean Tech Company", "path": "/awards?search=Bloom%20Energy"},
    {"name": "Commonwealth Fusion Systems", "aliases": ["commonwealth fusion", "cfs"], "org_type": "Clean Tech Startup", "path": "/awards?search=Commonwealth%20Fusion"},
    {"name": "TerraPower", "aliases": ["terrapower"], "org_type": "Nuclear Innovation", "path": "/awards?search=TerraPower"},
    {"name": "Kairos Power", "aliases": ["kairos power"], "org_type": "Nuclear Innovation", "path": "/awards?search=Kairos%20Power"},
    {"name": "First Solar", "aliases": ["first solar"], "org_type": "Solar Manufacturer", "path": "/awards?search=First%20Solar"},
    {"name": "Tesla Energy", "aliases": ["tesla energy", "megapack"], "org_type": "Energy Technology", "path": "/awards?search=Tesla"},
    {"name": "Subsea7", "aliases": ["subsea7", "subsea 7"], "org_type": "Offshore Engineering", "path": "/awards?search=Subsea7"}
]

KNOWN_POLICIES = [
    {"code": "NFPA-855", "title": "NFPA 855: Standard for the Installation of Stationary Energy Storage Systems", "keywords": ["nfpa 855", "nfpa855"], "path": "/dockets?search=NFPA-855"},
    {"code": "UL-9540A", "title": "UL 9540A: Test Method for Evaluating Thermal Runaway Fire Propagation", "keywords": ["ul 9540a", "ul9540a", "ul 9540"], "path": "/dockets?search=UL-9540A"},
    {"code": "FERC-ORDER-1920", "title": "FERC Order 1920: Regional Transmission Planning and Cost Allocation", "keywords": ["order 1920", "ferc order 1920", "regional transmission planning"], "path": "/dockets?search=FERC-1920"},
    {"code": "FERC-ORDER-2023", "title": "FERC Order 2023: Interconnection Queue Reform", "keywords": ["order 2023", "ferc order 2023", "interconnection queue"], "path": "/dockets?search=FERC-2023"},
    {"code": "IRA-SECTION-45V", "title": "IRA Section 45V: Clean Hydrogen Production Tax Credit", "keywords": ["45v", "section 45v", "clean hydrogen production tax credit"], "path": "/dockets?search=45V"},
    {"code": "IRA-SECTION-45X", "title": "IRA Section 45X: Advanced Manufacturing Production Credit", "keywords": ["45x", "section 45x", "advanced manufacturing production credit"], "path": "/dockets?search=45X"},
    {"code": "NYC-LOCAL-LAW-97", "title": "NYC Local Law 97: Building Carbon Cap & Emissions Mandates", "keywords": ["local law 97", "ll97", "building emissions cap"], "path": "/dockets?search=LL97"},
    {"code": "NY-CLCPA-70X30", "title": "New York CLCPA: 70% Renewable Electricity by 2030 Mandate", "keywords": ["clcpa", "climate leadership and community protection act", "70 by 30", "70x30"], "path": "/dockets?search=CLCPA"}
]

KNOWN_TECHNOLOGIES = [
    {"id": "iron_air_battery", "name": "Iron-Air Long-Duration Battery", "keywords": ["iron-air", "iron air", "form energy 100-hour", "multi-day storage"], "sector": "Long-Duration Energy Storage"},
    {"id": "flow_battery", "name": "Vanadium Redox Flow Battery", "keywords": ["vanadium flow", "redox flow", "iron-flow", "flow battery"], "sector": "Long-Duration Energy Storage"},
    {"id": "thermal_energy_network", "name": "Thermal Energy Networks & District Geothermal", "keywords": ["thermal energy network", "district geothermal", "district heating", "thermal loop"], "sector": "Building Decarbonization"},
    {"id": "pem_electrolyzer", "name": "Proton Exchange Membrane (PEM) Electrolyzer", "keywords": ["pem electrolyzer", "pem electrolysis", "proton exchange membrane electrolyzer"], "sector": "Clean Hydrogen"},
    {"id": "solid_oxide_electrolyzer", "name": "Solid Oxide Electrolyzer Cell (SOEC)", "keywords": ["solid oxide electrolyzer", "soec", "high temperature electrolysis"], "sector": "Clean Hydrogen"},
    {"id": "advanced_nuclear_smr", "name": "Small Modular Reactor (SMR) & Microreactors", "keywords": ["small modular reactor", "smr", "microreactor", "high-temperature gas reactor", "sodium-cooled fast reactor"], "sector": "Advanced Nuclear"},
    {"id": "magnetic_confinement_fusion", "name": "High-Field Magnetic Confinement Fusion", "keywords": ["magnetic confinement fusion", "fusion reactor", "high-temperature superconducting magnet", "tokamak", "sparc"], "sector": "Advanced Nuclear"},
    {"id": "floating_offshore_wind", "name": "Deep-Water Floating Offshore Wind Substructures", "keywords": ["floating offshore wind", "floating foundation", "semi-submersible wind", "taut-leg mooring"], "sector": "Renewable Generation"},
    {"id": "perovskite_tandem_pv", "name": "Perovskite-Silicon Tandem Photovoltaics", "keywords": ["perovskite", "perovskite tandem", "tandem cell", "high-efficiency pv"], "sector": "Renewable Generation"},
    {"id": "virtual_power_plant", "name": "Distributed VPP & Grid Edge DERMS Controller", "keywords": ["virtual power plant", "vpp", "derms", "distributed energy resource management", "ferc 2222"], "sector": "Grid Modernization"},
    {"id": "direct_air_capture", "name": "Solid Sorbent Direct Air Carbon Capture (DAC)", "keywords": ["direct air capture", "dac", "megaton dac hub", "solid sorbent dac"], "sector": "Industrial Decarbonization"}
]


def normalize_canonical_url(url: str) -> str:
    """Strip query tracking parameters and normalizes canonical URL for strict deduplication."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        filtered_query = []
        if parsed.query:
            qs = parse_qs(parsed.query, keep_blank_values=False)
            ignore_params = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid", "ref", "source", "feed", "rss"}
            for k, v in qs.items():
                if k.lower() not in ignore_params:
                    for val in v:
                        filtered_query.append((k, val))
        
        clean_path = parsed.path.rstrip("/")
        if not clean_path:
            clean_path = "/"
            
        clean_url = urlunparse((
            parsed.scheme.lower() or "https",
            parsed.netloc.lower().replace("www.", ""),
            clean_path,
            "",
            urlencode(filtered_query),
            ""
        ))
        return clean_url
    except Exception:
        return url.strip().lower()


def compute_content_fingerprint(title: str, url: str) -> str:
    """Generate SHA-256 fingerprint from normalized title and canonical URL."""
    clean_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
    canonical_url = normalize_canonical_url(url)
    raw = f"{clean_title}::{canonical_url}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]


def clean_and_shorten_headline(raw_title: str, raw_content: str = "", source_name: str = "", use_ai: bool = False) -> str:
    """
    Cleans, declutters, and shortens news headlines into punchy, Bloomberg-terminal style titles.
    Removes publisher suffixes, clickbait, trailing fluff, and utilizes OpenAI if explicitly requested.
    """
    if not raw_title:
        return ""

    # 1. Strip HTML entities and tags
    text = re.sub(r'<[^>]+>', '', raw_title).strip()
    text = (
        text.replace('&amp;', '&')
        .replace('&quot;', '"')
        .replace('&#039;', "'")
        .replace('&apos;', "'")
        .replace('&nbsp;', ' ')
    )

    # 2. Strip publisher suffixes (e.g. " | Canary Media", " - Utility Dive", " ...")
    suffixes_to_strip = [
        r'\s*\|\s*.*$',
        r'\s*-\s*(Canary Media|Utility Dive|CleanTechnica|Energy Storage News|GreenBiz|Trellis|Reuters|Bloomberg|NREL|DOE|FERC|NYSERDA|MassCEC|EERE|TechCrunch|PV Magazine|Solar Power World|Grist|RTO Insider|Power Grid).*$',
        r'\s*–\s*.*$',
        r'\s*—\s*.*$',
        r'\s*\[.*?\]$',
        r'\s*\(UPDATED\)$',
        r'\s*\(Exclusive\)$',
        r'\s*\.\.\.$',
        r'\s*…$'
    ]
    for pattern in suffixes_to_strip:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

    # 3. Strip clickbait prefixes
    prefixes_to_strip = [
        r'^(Exclusive|Breaking|Report|Analysis|Opinion|Watch|Listen|Update):\s*',
        r'^(Here\'s why|Why|How|What)\s+',
    ]
    for pattern in prefixes_to_strip:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

    # 4. If OpenAI is explicitly requested, generate an ultra-clean, concise Bloomberg headline (7-12 words)
    if use_ai and settings.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            prompt = f"""Rewrite this energy innovation news headline into a concise, punchy Bloomberg-terminal style headline (7 to 12 words max).
Make it factual, crisp, and direct. Focus on the core company, technology, funding amount, or regulatory action.
Do NOT use quotes, colon prefixes, or markdown asterisks.

Raw Headline: {text}
Clean Headline:"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.1,
            )
            cleaned = response.choices[0].message.content.strip().replace('"', '').replace('**', '').rstrip('.')
            if 15 <= len(cleaned) <= 120 and len(cleaned.split()) <= 15:
                return cleaned
        except Exception as e:
            logger.debug(f"OpenAI headline rewrite fallback: {e}")

    # 5. Algorithmic shortening fallback if too long
    words = text.split()
    if len(words) > 13:
        if ":" in text:
            parts = text.split(":")
            if len(parts[1].split()) >= 4:
                text = parts[1].strip()
            else:
                text = parts[0].strip()
        words = text.split()
        if len(words) > 12:
            text = " ".join(words[:12]).rstrip(",;:-")

    if text:
        text = text[0].upper() + text[1:]
    return text.strip()


def check_energy_innovation_relevance(title: str, content: str = "") -> Tuple[bool, float, str]:
    """Strict filter evaluating whether a news item focuses on clean energy innovation."""
    text = f"{title} {content}".lower()
    
    disqualifiers = [
        "celebrity", "hollywood", "nba", "nfl", "mlb", "crypto token", "meme coin",
        "oil drilling expansion", "crude oil pipeline spill", "gasoline pump prices"
    ]
    if any(d in text for d in disqualifiers):
        has_override = any(kw in text for kw in ["clean energy", "storage", "battery", "hydrogen", "renewable", "nyserda", "arpa-e"])
        if not has_override:
            return False, 0.0, "Irrelevant"

    matched_categories = {}
    total_matches = 0
    for cat, keywords in ENERGY_INNOVATION_TAXONOMY.items():
        cat_matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))
        if cat_matches > 0:
            matched_categories[cat] = cat_matches
            total_matches += cat_matches

    if not matched_categories and total_matches == 0:
        general_terms = ["clean energy", "renewable energy", "climate tech", "clean grant", "zero emission", "decarbonization", "energy transition"]
        gen_matches = sum(1 for gt in general_terms if gt in text)
        if gen_matches >= 1:
            return True, 0.70, "Clean Energy Innovation"
        return False, 0.0, "Irrelevant"

    best_cat = max(matched_categories.items(), key=lambda x: x[1])[0]
    score = min(1.0, 0.75 + (matched_categories[best_cat] * 0.08))
    return True, score, best_cat


def classify_news_sentiment(title: str, text: str = "") -> str:
    """Determines sentiment / commercial intelligence stage classification."""
    combined = f"{title} {text}".lower()
    if any(k in combined for k in ["grant awarded", "awarded", "grant won", "receives $", "secures $", "foa", "pon ", "funding from", "award"]):
        return "grant_awarded"
    if any(k in combined for k in ["series a", "series b", "series c", "growth equity", "raises $", "closes $", "venture capital", "funding round"]):
        return "funding_round"
    if any(k in combined for k in ["breakthrough", "world record", "efficiency record", "discovery", "first-of-a-kind", "foak", "unveils", "milestone"]):
        return "breakthrough"
    if any(k in combined for k in ["commercial operation", "cod", "groundbreaking", "commissioned", "grid-connected", "begins construction", "opens factory"]):
        return "commercial"
    if any(k in combined for k in ["ferc order", "order 1920", "order 2023", "rule finalized", "finalizes", "mandate", "standard approved", "standard update", "nfpa", "ul standard", "rate case approved", "regulatory", "rulemaking", "puc"]):
        return "regulatory"
    if any(k in combined for k in ["partnership", "teams with", "consortium", "mou", "agreement"]):
        return "milestone"
    return "neutral"


def synthesize_llm_summary(title: str, raw_content: str, category_tag: str, linked_entities: List[Dict[str, Any]]) -> str:
    """Generates a very brief LLM executive summary (1-2 sentences) in Bloomberg Terminal format."""
    cleaned_content = re.sub(r'<[^>]+>', '', raw_content or '').strip()
    
    # Try OpenAI if configured
    if settings.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            entity_context = ", ".join([f"{e['element_type'].upper()}: {e['element_title']}" for e in linked_entities[:3]])
            prompt = f"""Synthesize a 1-2 sentence Bloomberg Terminal style executive briefing for this energy innovation news story.
Focus strictly on the specific technology innovation, grant award, or policy milestone and why it matters to clean tech performers.
Title: {title}
Category: {category_tag}
Linked Database Entities: {entity_context}
Snippet: {cleaned_content[:350]}

Format: Pure, high-density professional prose. Strictly do NOT use bold text (no **). 1 to 2 sentences maximum."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.2,
            )
            summary = response.choices[0].message.content.strip().replace("**", "")
            if len(summary) > 20:
                return summary
        except Exception as e:
            logger.debug(f"OpenAI summary fallback: {e}")

    # Grounded synthesis fallback
    primary_entity = linked_entities[0]["element_title"] if linked_entities else category_tag
    rationale = linked_entities[0]["link_rationale"] if linked_entities else "Advances upstream clean energy technology commercialization."
    
    if len(cleaned_content) > 60:
        first_sentence = cleaned_content.split(". ")[0].strip()
        if not first_sentence.endswith("."):
            first_sentence += "."
        return f"{first_sentence} In the database, this connects to {primary_entity} ({rationale.lower()})."
    else:
        return f"{title}. Directly relevant to database assets in {category_tag} ({primary_entity})."


def resolve_database_linkages(
    title: str,
    raw_content: str,
    db: Session
) -> List[Dict[str, Any]]:
    """
    Matches article text strictly against specific database elements:
    - Opportunity (PONs, FOAs, RFPs)
    - Organization (Agencies, Utilities, Performers)
    - Program (Funding Portfolios)
    - Award / Recipient (Grants Ledger)
    - Technology (Frontier Subsystems)
    - Policy (Standards & Dockets)
    Returns ONLY specific, high-confidence entity linkages (no vague fallbacks).
    """
    full_text = f"{title} {raw_content}".lower()
    links: List[Dict[str, Any]] = []
    seen_keys = set()

    def add_link(elem_type: str, elem_id: str, title_str: str, url_path: str, rationale: str, conf: float = 1.0):
        key = f"{elem_type}:{elem_id}"
        if key in seen_keys:
            return
        seen_keys.add(key)
        links.append({
            "element_type": elem_type,
            "element_id": str(elem_id),
            "element_title": title_str,
            "element_url_path": url_path,
            "link_rationale": rationale,
            "confidence_score": conf
        })

    # 1. Match Specific Policies, Statutory Standards & Proceedings
    for pol in KNOWN_POLICIES:
        if any(kw in full_text for kw in pol["keywords"]):
            add_link(
                "policy",
                pol["code"],
                pol["title"],
                pol["path"],
                f"Directly establishes compliance and testing requirements for {pol['code']}.",
                0.98
            )

    # 2. Match Specific Clean Technologies & Subsystems
    for tech in KNOWN_TECHNOLOGIES:
        if any(kw in full_text for kw in tech["keywords"]):
            add_link(
                "technology",
                tech["id"],
                tech["name"],
                f"/technologies?tech={tech['id']}",
                f"Covers frontier research and commercial performance benchmarks in {tech['sector']}.",
                0.96
            )

    # 3. Match Specific Organizations & Funders
    for org in KNOWN_ORGANIZATIONS:
        if any(re.search(r'\b' + re.escape(alias) + r'\b', full_text) for alias in org["aliases"]):
            add_link(
                "organization",
                org["name"],
                f"{org['name']} ({org['org_type']})",
                org["path"],
                f"Features {org['name']} active procurement, investment, or regulatory initiative.",
                0.94
            )

    # 4. Match Opportunities / Solicitations (e.g., PON 6141, PON 6037, PON 5989, DE-FOA-0003348)
    pon_matches = re.findall(r'\b(PON\s*\d{4,5}|DE-FOA-\d{7}|GFO-\d{2}-\d{3})\b', full_text, re.IGNORECASE)
    for pon_match in pon_matches:
        clean_pon = re.sub(r'\s+', ' ', pon_match.upper())
        from app.models.opportunity import Opportunity
        opp = db.query(Opportunity).filter(
            or_(
                Opportunity.solicitation_number.ilike(f"%{clean_pon}%"),
                Opportunity.name.ilike(f"%{clean_pon}%")
            )
        ).first()
        if opp:
            add_link(
                "opportunity",
                str(opp.id),
                f"{opp.solicitation_number}: {opp.name[:60]}",
                f"/opportunities?id={opp.id}",
                f"Explicit funding solicitation: {opp.agency} allocation ({opp.solicitation_number}).",
                1.0
            )

    # Flagship Solicitations by Keyword
    flagship_opps = [
        ("Long-Duration Energy Storage", "PON 6141", "PON 6141: High-Capacity Grid Energy Storage"),
        ("Thermal Energy Networks", "PON 6037", "PON 6037: Community Heat Pumps & Thermal Loops"),
        ("Future Grid Challenge", "PON 4192", "PON 4192: Future Grid Challenge for Utilities"),
        ("Buildings of Excellence", "PON 5989", "PON 5989: Zero-Emissions Buildings Competition"),
        ("Offshore Wind Supply Chain", "PON 6088", "PON 6088: Offshore Wind Ports & Infrastructure"),
        ("Clean Transportation Prizes", "PON 5437", "PON 5437: NY Clean Transportation Prizes")
    ]
    for search_kw, sol_num, desc_title in flagship_opps:
        if search_kw.lower() in full_text:
            from app.models.opportunity import Opportunity
            opp = db.query(Opportunity).filter(Opportunity.solicitation_number.ilike(f"%{sol_num}%")).first()
            if opp:
                add_link(
                    "opportunity",
                    str(opp.id),
                    f"{opp.solicitation_number}: {opp.name[:60]}",
                    f"/opportunities?id={opp.id}",
                    f"Aligned with {opp.agency} target funding solicitation ({opp.solicitation_number}).",
                    0.90
                )

    # 5. Match Programs in database
    from app.models.program import Program
    for prog in db.query(Program).limit(20).all():
        if prog.name and len(prog.name) > 6 and prog.name.lower() in full_text:
            add_link(
                "program",
                str(prog.id),
                prog.name,
                f"/programs?search={prog.name}",
                f"Connected to funding portfolio initiative ({prog.name}).",
                0.88
            )

    # Sort links by confidence score descending
    links.sort(key=lambda x: x["confidence_score"], reverse=True)
    return links


def synthesize_regulatory_commercial_impact(
    item_type: str,
    identifier: str,
    title: str,
    summary: str,
    mandate_or_tailwinds: str,
    friction_points: Optional[str] = None,
    linked_technologies: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Synthesizes institutional commercial impact analysis for regulatory dockets, PSC proceedings,
    and statutory standards using multi-provider LLM (OpenAI, Gemini, Claude) with deterministic fallback.
    """
    tech_str = ", ".join(linked_technologies) if linked_technologies else "Clean Energy Technologies"
    
    # Check for API keys
    import os
    import json
    openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
    gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
    anthropic_key = getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY")

    prompt = f"""You are a senior regulatory strategist and clean energy infrastructure investment director.
Perform a deep commercial impact synthesis for the following {item_type.upper()}:

IDENTIFIER: {identifier}
TITLE: {title}
EXECUTIVE SUMMARY: {summary}
MANDATE / TAILWINDS: {mandate_or_tailwinds}
FRICTION POINTS & RISKS: {friction_points or 'Standard utility regulatory review cycles.'}
RELEVANT TECHNOLOGIES: {tech_str}

Please generate a structured commercial diligence brief:
1. "impacted_stakeholders": List of 3-5 specific affected institutional stakeholder classes (e.g. "Independent Power Producers", "Distribution Utilities", "Hyperscale Data Center Offtakers", "Tax Equity Investors").
2. "bottlenecks_and_risks": List of 2-4 critical commercial, interconnection, or compliance bottlenecks.
3. "monetization_pathways": List of 2-4 concrete revenue, cost-recovery, or incentive monetization pathways unlocked.
4. "executive_synthesis": 2-3 paragraph executive diligence briefing on how project sponsors and capital providers should navigate this docket/standard.

Return ONLY a JSON object matching this schema:
{{
  "impacted_stakeholders": ["...", "..."],
  "bottlenecks_and_risks": ["...", "..."],
  "monetization_pathways": ["...", "..."],
  "executive_synthesis": "..."
}}"""

    # 1. Try OpenAI
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=25.0, max_retries=2)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regulatory and infrastructure finance intelligence analyst. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=900,
            )
            parsed = json.loads(resp.choices[0].message.content or "{}")
            if parsed and "executive_synthesis" in parsed:
                parsed["status"] = "success"
                parsed["synthesized_by"] = "OpenAI GPT-4o-mini"
                return parsed
        except Exception as e:
            logger.warning(f"OpenAI regulatory impact synthesis failed: {e}")

    # 2. Try Gemini
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                )
            )
            parsed = json.loads(response.text or "{}")
            if parsed and "executive_synthesis" in parsed:
                parsed["status"] = "success"
                parsed["synthesized_by"] = "Google Gemini 2.5 Flash"
                return parsed
        except Exception as e:
            logger.warning(f"Gemini regulatory impact synthesis failed: {e}")

    # 3. Try Anthropic
    if anthropic_key:
        try:
            import urllib.request
            req_data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 900,
                "temperature": 0.2,
                "system": "You are a regulatory and infrastructure finance intelligence analyst. Return ONLY valid JSON.",
                "messages": [{"role": "user", "content": prompt}]
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25.0) as r:
                res_json = json.loads(r.read().decode("utf-8"))
                content_block = res_json.get("content", [{}])[0].get("text", "{}")
                parsed = json.loads(content_block)
                if parsed and "executive_synthesis" in parsed:
                    parsed["status"] = "success"
                    parsed["synthesized_by"] = "Anthropic Claude 3.5 Sonnet"
                    return parsed
        except Exception as e:
            logger.warning(f"Anthropic regulatory impact synthesis failed: {e}")

    # Deterministic Rule-Based Fallback
    stakeholders = ["Clean Energy Project Sponsors", "Regulated Electric & Gas Utilities", "Infrastructure Funds & Tax Equity", "State Energy Regulators"]
    if "interconnection" in f"{title} {summary}".lower():
        stakeholders.append("RTO/ISO Transmission Planners")
    elif "hydrogen" in f"{title} {summary}".lower() or "fuel" in f"{title} {summary}".lower():
        stakeholders.append("Industrial Offtakers & Chemical Processors")

    bottlenecks = []
    if friction_points:
        bottlenecks.append(friction_points.strip())
    else:
        bottlenecks.append("Protracted administrative review cycles and multi-year utility queue study backlog.")
    bottlenecks.append(f"Statutory compliance verification timelines under {identifier} mandates.")

    pathways = [
        f"Accelerated permitting and interconnection clearance under {identifier} provisions.",
        f"Alignment with utility rate base capital expenditures and statutory clean energy procurements."
    ]
    if mandate_or_tailwinds:
        pathways.append(f"Direct participation in programs enabled by: {mandate_or_tailwinds[:120]}...")

    exec_synth = (
        f"{title} ({identifier}) establishes critical ground rules for {tech_str}. "
        f"Primary regulatory mandates require asset developers to satisfy rigorous technical and compliance benchmarks ({mandate_or_tailwinds[:150]}). "
        f"Project sponsors must proactively address key friction points including {bottlenecks[0]} while structuring commercial contracts to capitalize on emerging utility rate base and incentive mechanisms."
    )

    return {
        "status": "success",
        "synthesized_by": "Rule-Based Deterministic Fallback",
        "impacted_stakeholders": stakeholders,
        "bottlenecks_and_risks": bottlenecks,
        "monetization_pathways": pathways,
        "executive_synthesis": exec_synth
    }

