"""Complete all data enrichment: FTS rebuild, keywords extraction, funding enrichment, relationship detection."""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import SessionLocal, engine
from app.models.opportunity import Opportunity
from sqlalchemy import text, func

db = SessionLocal()

# ============================================================
# 1. EXTRACT KEYWORDS FROM DESCRIPTIONS
# ============================================================
print("=== STEP 1: Extracting keywords from descriptions ===")

KEYWORD_MAP = {
    "solar": "Solar", "photovoltaic": "Solar", "pv": "Solar",
    "wind": "Wind", "offshore wind": "Wind", "wind turbine": "Wind",
    "battery": "Energy Storage", "energy storage": "Energy Storage", "storage": "Energy Storage",
    "long duration storage": "Energy Storage",
    "hydrogen": "Hydrogen", "fuel cell": "Hydrogen", "electrolysis": "Hydrogen",
    "electrolyzer": "Hydrogen",
    "grid": "Grid Modernization", "smart grid": "Grid Modernization",
    "microgrid": "Grid Modernization", "transmission": "Grid Modernization",
    "distribution": "Grid Modernization", "demand response": "Grid Modernization",
    "nuclear": "Nuclear", "fusion": "Nuclear", "fission": "Nuclear",
    "small modular reactor": "Nuclear", "advanced reactor": "Nuclear",
    "carbon capture": "Carbon Management", "ccs": "Carbon Management",
    "ccus": "Carbon Management", "direct air capture": "Carbon Management",
    "carbon sequestration": "Carbon Management", "carbon dioxide removal": "Carbon Management",
    "electric vehicle": "Clean Transportation", "ev charging": "Clean Transportation",
    "clean transportation": "Clean Transportation",
    "building energy": "Building Efficiency", "energy efficiency": "Building Efficiency",
    "heat pump": "Building Efficiency", "weatherization": "Building Efficiency",
    "hvac": "Building Efficiency", "building envelope": "Building Efficiency",
    "building decarbonization": "Building Efficiency",
    "biofuel": "Bioenergy", "bioenergy": "Bioenergy", "biomass": "Bioenergy",
    "biogas": "Bioenergy", "sustainable aviation fuel": "Bioenergy",
    "renewable natural gas": "Bioenergy",
    "geothermal": "Geothermal",
    "industrial decarbonization": "Industrial", "process heat": "Industrial",
    "industrial emissions": "Industrial", "manufacturing": "Industrial",
    "climate change": "Climate", "greenhouse gas": "Climate", "ghg": "Climate",
    "climate mitigation": "Climate", "net zero": "Climate",
    "decarbonization": "Climate", "zero emission": "Climate",
    "electrification": "Electrification",
    "renewable energy": "Renewables", "clean energy": "Renewables",
    "distributed energy": "Distributed Energy",
    "combined heat and power": "CHP", "cogeneration": "CHP",
    "cybersecurity": "Grid Cybersecurity",
    "resilience": "Resilience", "resilient": "Resilience",
    "workforce": "Workforce", "training": "Workforce",
}

updated_kw = 0
opps = db.query(Opportunity).filter(
    (Opportunity.keywords == None) | (Opportunity.keywords == "")
).all()

for opp in opps:
    text_content = f"{opp.name or ''} {opp.short_description or ''}".lower()
    found = set()
    for term, category in KEYWORD_MAP.items():
        if term in text_content:
            found.add(category)
    if found:
        opp.keywords = ", ".join(sorted(found))
        updated_kw += 1

db.commit()
print(f"  Keywords extracted for {updated_kw} opportunities")

# ============================================================
# 2. ENRICH TOTAL FUNDING FROM DESCRIPTIONS
# ============================================================
print("\n=== STEP 2: Extracting total funding from descriptions ===")

updated_funding = 0
opps = db.query(Opportunity).filter(Opportunity.total_funding == None).all()

for opp in opps:
    desc = opp.short_description or ""
    name = opp.name or ""
    text_content = f"{name} {desc}"
    
    # Look for dollar amounts like "$50 million", "$2.5M", "$100,000,000"
    patterns = [
        r'\$\s*([\d,.]+)\s*billion',
        r'\$\s*([\d,.]+)\s*million',
        r'\$\s*([\d,.]+)\s*M\b',
        r'\$\s*([\d,.]+)\s*B\b',
        r'([\d,.]+)\s*billion\s*(?:dollars?|USD)',
        r'([\d,.]+)\s*million\s*(?:dollars?|USD)',
        r'total\s+(?:program\s+)?funding[:\s]+\$\s*([\d,.]+)',
        r'up\s+to\s+\$\s*([\d,.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1).replace(",", ""))
                if "billion" in pattern.lower() or pattern.endswith("B\\b"):
                    val *= 1_000_000_000
                elif "million" in pattern.lower() or pattern.endswith("M\\b"):
                    val *= 1_000_000
                if val > 0:
                    opp.total_funding = val
                    updated_funding += 1
                    break
            except ValueError:
                pass

db.commit()
print(f"  Funding extracted for {updated_funding} opportunities")

# ============================================================
# 3. SET DATA PROVENANCE WHERE MISSING
# ============================================================
print("\n=== STEP 3: Setting data provenance ===")

updated_prov = db.query(Opportunity).filter(Opportunity.data_provenance == None).update(
    {"data_provenance": "observed"}, synchronize_session=False
)
db.commit()
print(f"  Provenance set for {updated_prov} opportunities")

# ============================================================
# 4. REBUILD FTS INDEXES
# ============================================================
print("\n=== STEP 4: Rebuilding FTS indexes ===")

with engine.connect() as conn:
    conn.execute(text("DELETE FROM opportunities_fts"))
    conn.execute(text(
        "INSERT INTO opportunities_fts(rowid, solicitation_number, name, short_description) "
        "SELECT id, solicitation_number, name, COALESCE(short_description, '') FROM opportunities"
    ))
    conn.execute(text("DELETE FROM historical_projects_fts"))
    conn.execute(text(
        "INSERT INTO historical_projects_fts(rowid, project_title, contractor_name, project_description, technology_1, technology_2, technology_3) "
        "SELECT id, project_title, COALESCE(contractor_name, ''), COALESCE(project_description, ''), "
        "COALESCE(technology_1, ''), COALESCE(technology_2, ''), COALESCE(technology_3, '') FROM historical_projects"
    ))
    conn.execute(text("DELETE FROM programs_fts"))
    conn.execute(text(
        "INSERT INTO programs_fts(rowid, name, description) "
        "SELECT id, name, COALESCE(description, '') FROM programs"
    ))
    conn.commit()

fts_count = db.execute(text("SELECT COUNT(*) FROM opportunities_fts")).scalar()
print(f"  FTS indexed: {fts_count} opportunities")

# ============================================================
# 5. DETECT RELATIONSHIPS
# ============================================================
print("\n=== STEP 5: Detecting opportunity relationships ===")

try:
    from app.engine.relationships import detect_relationships
    rel_stats = detect_relationships(db)
    print(f"  Relationships: {rel_stats}")
except Exception as e:
    print(f"  Relationship detection failed: {e}")
    # Manual fallback: detect recurring opportunities (same agency + similar name)
    print("  Running fallback relationship detection...")
    
    from app.models.relationship import OpportunityRelationship
    
    # Find recurring programs: same agency, similar solicitation number pattern
    opps_by_agency = {}
    all_opps = db.query(Opportunity).filter(Opportunity.agency != None).all()
    for opp in all_opps:
        key = opp.agency
        if key not in opps_by_agency:
            opps_by_agency[key] = []
        opps_by_agency[key].append(opp)
    
    rel_count = 0
    for agency, agency_opps in opps_by_agency.items():
        if len(agency_opps) < 2:
            continue
        
        # Group by base solicitation pattern (strip year/version suffixes)
        groups = {}
        for opp in agency_opps:
            sol = opp.solicitation_number or ""
            # Strip trailing year patterns, version numbers
            base = re.sub(r'[-_]?(20\d{2}|FY\d{2,4}|V\d+|Round\s*\d+).*$', '', sol, flags=re.IGNORECASE).strip()
            if not base or len(base) < 4:
                base = opp.name or ""
                base = re.sub(r'\b20\d{2}\b.*$', '', base).strip()[:60]
            if base:
                if base not in groups:
                    groups[base] = []
                groups[base].append(opp)
        
        for base, group in groups.items():
            if len(group) < 2:
                continue
            # Sort by year
            group.sort(key=lambda o: o.year or 0)
            for i in range(len(group) - 1):
                # Check if relationship already exists
                existing = db.query(OpportunityRelationship).filter_by(
                    source_opp_id=group[i].id,
                    target_opp_id=group[i+1].id
                ).first()
                if not existing:
                    rel = OpportunityRelationship(
                        source_opp_id=group[i].id,
                        target_opp_id=group[i+1].id,
                        relationship_type="recurring",
                        confidence=0.7,
                        rationale=f"Same program base: {base[:100]}",
                        is_inferred=True,
                    )
                    db.add(rel)
                    rel_count += 1
    
    db.commit()
    print(f"  Fallback detected {rel_count} recurring relationships")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("  ENRICHMENT COMPLETE")
print("=" * 60)
total = db.query(Opportunity).count()
with_kw = db.query(Opportunity).filter(Opportunity.keywords != None, Opportunity.keywords != "").count()
with_fund = db.query(Opportunity).filter(Opportunity.total_funding != None).count()
with_prov = db.query(Opportunity).filter(Opportunity.data_provenance != None).count()
fts = db.execute(text("SELECT COUNT(*) FROM opportunities_fts")).scalar()
rels = db.execute(text("SELECT COUNT(*) FROM opportunity_relationships")).scalar()

print(f"  Total opportunities:  {total}")
print(f"  Keywords populated:   {with_kw}/{total} ({100*with_kw//total}%)")
print(f"  Funding populated:    {with_fund}/{total} ({100*with_fund//total}%)")
print(f"  Provenance populated: {with_prov}/{total} ({100*with_prov//total}%)")
print(f"  FTS indexed:          {fts}/{total}")
print(f"  Relationships:        {rels}")
print("=" * 60)

db.close()
