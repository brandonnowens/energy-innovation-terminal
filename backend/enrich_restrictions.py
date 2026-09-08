"""Create the opportunity_restrictions table and populate from existing data."""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import engine, SessionLocal
from app.models.opportunity import Opportunity, OpportunityRestriction, EligibilityRule
from sqlalchemy import text, inspect

# ============================================================
# 1. CREATE TABLE
# ============================================================
print("=== Step 1: Create opportunity_restrictions table ===")
insp = inspect(engine)
existing = set(insp.get_table_names())

if "opportunity_restrictions" not in existing:
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE opportunity_restrictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
                category VARCHAR(50) NOT NULL,
                title VARCHAR(300) NOT NULL,
                description TEXT,
                severity VARCHAR(20) DEFAULT 'hard',
                source VARCHAR(200),
                source_text TEXT,
                source_url VARCHAR(500),
                data_provenance VARCHAR(50) DEFAULT 'observed',
                confidence REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("CREATE INDEX ix_restriction_oppid ON opportunity_restrictions(opportunity_id)"))
        conn.execute(text("CREATE INDEX ix_restriction_cat ON opportunity_restrictions(category)"))
        conn.commit()
    print("  Created table")
else:
    print("  Already exists")

# ============================================================
# 2. EXTRACT RESTRICTIONS FROM EXISTING DATA
# ============================================================
print("\n=== Step 2: Extract restrictions from existing opportunities ===")

db = SessionLocal()

# Common federal restriction patterns found in DOE/NSF/EPA FOAs
FEDERAL_RESTRICTIONS = {
    "DOE": [
        ("lobbying", "Anti-Lobbying", "Appropriated funds may not be used to influence or attempt to influence an officer or employee of any agency, Member of Congress, or staff.", "hard"),
        ("procurement", "Buy American / Domestic Content", "Equipment and products must comply with Build America Buy America (BABA) Act requirements for federally funded projects.", "hard"),
        ("cost_share", "Cost Share Required", "Non-federal cost share is typically required, ranging from 20-50% depending on technology readiness level.", "hard"),
        ("reporting", "Reporting Requirements", "Quarterly progress reports, annual reports, and a final technical report are required. Financial reports due per Federal Financial Report (FFR) schedule.", "hard"),
        ("environmental", "NEPA Compliance", "Projects must comply with the National Environmental Policy Act (NEPA). Environmental review required before expenditure of federal funds on construction or site-specific activities.", "hard"),
        ("ip", "March-in Rights / IP", "Government retains a nonexclusive, irrevocable, paid-up license to practice inventions made under the award. Subject inventions must be reported.", "soft"),
        ("conflict_of_interest", "Organizational COI", "Recipients must disclose any actual or potential conflicts of interest. Organizational conflicts of interest may disqualify applicants.", "hard"),
        ("use_of_funds", "No Construction (R&D)", "Funds may generally not be used for construction of buildings or facilities unless specifically authorized in the FOA.", "hard"),
    ],
    "ARPA-E": [
        ("lobbying", "Anti-Lobbying", "Appropriated funds may not be used for lobbying activities.", "hard"),
        ("procurement", "Domestic Manufacture", "Products developed with ARPA-E funding must be substantially manufactured in the United States.", "hard"),
        ("cost_share", "Cost Share Required", "Minimum 20% non-federal cost share required for all ARPA-E awards.", "hard"),
        ("ip", "IP / Data Rights", "Government receives unlimited rights in technical data and software produced. March-in rights apply to subject inventions.", "hard"),
        ("reporting", "Milestone Reporting", "Quarterly technical and financial reports required. Go/no-go milestones with potential project termination.", "hard"),
        ("prior_awards", "No Duplicative Funding", "Cannot receive funding for the same scope of work from multiple federal sources.", "hard"),
    ],
    "NSF": [
        ("applicant", "PI Eligibility", "Principal Investigators must hold a position at an eligible US institution. Foreign institutions are generally ineligible as lead.", "hard"),
        ("cost_share", "Cost Share Policy", "NSF does not require cost sharing unless explicitly stated in the solicitation. Voluntary committed cost sharing is not permitted.", "info"),
        ("reporting", "Annual & Final Reports", "Annual project reports required via Research.gov. Final project report due within 120 days of award expiration.", "hard"),
        ("use_of_funds", "No Construction", "NSF funds generally cannot be used for construction of research facilities.", "hard"),
        ("prior_awards", "Current & Pending Support", "All current and pending support must be disclosed. Overlap with other federal awards is prohibited.", "hard"),
        ("ip", "Data Sharing", "NSF expects significant findings to be promptly submitted for publication with appropriate acknowledgment.", "soft"),
    ],
    "EPA": [
        ("applicant", "Non-Profit / Government Only", "Many EPA grants are restricted to state/local governments, tribal governments, and non-profit organizations.", "hard"),
        ("lobbying", "Anti-Lobbying", "Federal funds may not be used for lobbying or influencing federal officials.", "hard"),
        ("reporting", "Performance Reporting", "Semi-annual or quarterly performance reports and annual financial reports required.", "hard"),
        ("environmental", "Environmental Compliance", "Projects must comply with applicable environmental laws including NEPA, Clean Air Act, Clean Water Act.", "hard"),
    ],
    "Gates Foundation": [
        ("geographic", "Global Focus", "Gates Foundation energy grants typically target developing countries and global access to energy, not US domestic projects.", "soft"),
        ("use_of_funds", "Charitable Purpose", "Funds must be used exclusively for charitable, scientific, or educational purposes.", "hard"),
        ("reporting", "Progress Reporting", "Grantees must provide regular progress reports and financial accountings as specified in the grant agreement.", "hard"),
    ],
}

# State agency restrictions
STATE_RESTRICTIONS = {
    "NYSERDA": [
        ("geographic", "New York State", "Project must be located in or primarily benefit New York State.", "hard"),
        ("applicant", "NY-Based Entities Preferred", "Applicants must be authorized to do business in New York State.", "hard"),
        ("cost_share", "Cost Share", "Cost sharing requirements vary by program; typically 50% for commercial entities, lower for academic/nonprofit.", "soft"),
    ],
    "CEC": [
        ("geographic", "California", "Projects must be located in and primarily benefit California ratepayers.", "hard"),
        ("procurement", "CA Prevailing Wage", "Construction-related work must comply with California prevailing wage requirements.", "hard"),
    ],
    "MassCEC": [
        ("geographic", "Massachusetts", "Projects must be located in or primarily benefit Massachusetts.", "hard"),
    ],
}

# Technology-specific restrictions from descriptions
TECH_RESTRICTION_PATTERNS = [
    (r"(?:cannot|may not|shall not|prohibited from)\s+(?:use|spend|expend).*?(?:for|on)\s+(.{10,80})", "use_of_funds"),
    (r"(?:ineligible|not eligible|excluded).*?(?:entities?|organizations?|applicants?|companies|firms).*?(?:include|are|such as)\s+(.{10,100})", "applicant"),
    (r"(?:limited to|restricted to|only (?:available|open) to)\s+(.{10,80})", "applicant"),
    (r"(?:must be (?:located|sited|situated|based) in)\s+(.{10,60})", "geographic"),
    (r"(?:minimum|at least)\s+(\d+%?\s*(?:cost[- ]share|match|non-federal))", "cost_share"),
    (r"(?:maximum|up to)\s+(\d+)\s*(?:months?|years?)\s*(?:period of performance|project duration)", "time"),
    (r"(?:buy american|domestic content|manufactured in.*?united states|BABA)", "procurement"),
]

added_count = 0
opp_count = 0

# Apply agency-level restrictions
all_opps = db.query(Opportunity).all()
print(f"  Processing {len(all_opps)} opportunities...")

for opp in all_opps:
    restrictions_to_add = []
    agency = opp.agency or ""

    # Agency-level restrictions
    if agency in FEDERAL_RESTRICTIONS:
        for cat, title, desc, severity in FEDERAL_RESTRICTIONS[agency]:
            restrictions_to_add.append((cat, title, desc, severity, "Federal standard terms", agency))
    elif agency in STATE_RESTRICTIONS:
        for cat, title, desc, severity in STATE_RESTRICTIONS[agency]:
            restrictions_to_add.append((cat, title, desc, severity, "State program terms", agency))

    # Extract from description using patterns
    desc_text = opp.short_description or ""
    name_text = opp.name or ""
    full_text = f"{name_text} {desc_text}"

    for pattern, cat in TECH_RESTRICTION_PATTERNS:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches[:2]:  # Limit to 2 per pattern
            clean = match.strip().rstrip(".,;:")
            if len(clean) > 10:
                restrictions_to_add.append((
                    cat,
                    f"Restriction: {clean[:80]}",
                    clean,
                    "hard",
                    "Extracted from description",
                    opp.source_name,
                ))

    # Convert eligibility rules that are exclusions into restrictions
    for rule in opp.eligibility_rules:
        if rule.rule_operator in ("not", "excludes") or (rule.rule_key and "exclu" in rule.rule_key.lower()):
            cat_map = {
                "geography": "geographic",
                "applicant": "applicant",
                "technology": "technology",
                "trl": "technology",
                "exclusion": "applicant",
            }
            cat = cat_map.get(rule.rule_type, "other")
            restrictions_to_add.append((
                cat,
                f"{rule.rule_type}: {rule.rule_key} {rule.rule_operator} {rule.rule_value}",
                rule.source_text or f"{rule.rule_key} {rule.rule_operator} {rule.rule_value}",
                "hard" if rule.is_hard_requirement else "soft",
                rule.source or "Eligibility rule",
                opp.source_name,
            ))

    if restrictions_to_add:
        opp_count += 1
        for cat, title, desc, severity, source, source_name in restrictions_to_add:
            r = OpportunityRestriction(
                opportunity_id=opp.id,
                category=cat,
                title=title[:300],
                description=desc[:2000] if desc else None,
                severity=severity,
                source=source,
                data_provenance="observed",
                confidence=0.9 if source == "Federal standard terms" else 0.7,
            )
            db.add(r)
            added_count += 1

db.commit()
print(f"  Added {added_count} restrictions across {opp_count} opportunities")

# Summary by category
from sqlalchemy import func
cat_counts = db.query(
    OpportunityRestriction.category, func.count()
).group_by(OpportunityRestriction.category).order_by(func.count().desc()).all()

print(f"\n  By category:")
for cat, cnt in cat_counts:
    print(f"    {cat:<25} {cnt:>5}")

sev_counts = db.query(
    OpportunityRestriction.severity, func.count()
).group_by(OpportunityRestriction.severity).all()

print(f"\n  By severity:")
for sev, cnt in sev_counts:
    print(f"    {sev:<10} {cnt:>5}")

db.close()
print("\nDone!")
