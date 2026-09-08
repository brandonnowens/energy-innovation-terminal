"""
Comprehensive relationship discovery engine.
Discovers real linkages from the data — nothing invented.

Relationship types:
  - recurring: Same program reissued across years (same agency, similar name/sol number)
  - predecessor_successor: Sequential FOAs within the same program office
  - complementary: Different agencies funding the same technology area simultaneously
  - stackable: State + federal programs in same technology area (can be combined)
  - topical_cluster: Opportunities with highly overlapping keyword profiles
  - same_program_family: Share CFDA/assistance listing numbers or program names
"""
import sys, os, re
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import SessionLocal, engine
from app.models.opportunity import Opportunity
from app.models.relationship import OpportunityRelationship
from sqlalchemy import text, func

db = SessionLocal()

# Clear existing relationships to rebuild clean
print("Clearing existing relationships...")
db.execute(text("DELETE FROM opportunity_relationships"))
db.commit()

# Load all opportunities with key fields
print("Loading all opportunities...")
opps = db.query(Opportunity).all()
print(f"  Loaded {len(opps)} opportunities")

# Build lookup structures
by_id = {o.id: o for o in opps}
by_agency = defaultdict(list)
by_keyword = defaultdict(list)
by_year = defaultdict(list)
by_sol_base = defaultdict(list)

for o in opps:
    by_agency[o.agency].append(o)
    if o.year:
        by_year[o.year].append(o)
    
    # Parse keywords into a set
    kw_str = o.keywords or ""
    kw_set = set(k.strip() for k in kw_str.split(",") if k.strip())
    o._kw_set = kw_set
    for kw in kw_set:
        by_keyword[kw].append(o)

    # Extract solicitation base pattern (strip year/version/round suffixes)
    sol = o.solicitation_number or ""
    base = re.sub(r'[-_]?\b(20\d{2}|FY\d{2,4}|V\d+|Round\s*\d+|Cohort\s*\d+)\b.*$', '', sol, flags=re.IGNORECASE).strip()
    if base and len(base) >= 5:
        by_sol_base[(o.agency, base)].append(o)

relationships = []

def add_rel(source_id, target_id, rel_type, confidence, rationale, evidence=""):
    """Add a relationship if it doesn't duplicate."""
    # Normalize direction so we don't duplicate A->B and B->A
    s, t = min(source_id, target_id), max(source_id, target_id)
    key = (s, t)  # Only one relationship per pair (highest priority wins)
    if key not in seen_rels:
        seen_rels.add(key)
        relationships.append(OpportunityRelationship(
            source_opp_id=source_id,
            target_opp_id=target_id,
            relationship_type=rel_type,
            confidence=confidence,
            rationale=rationale[:500],
            evidence=evidence[:500] if evidence else None,
            is_inferred=True,
        ))

seen_rels = set()

# ============================================================
# 1. RECURRING: Same solicitation base pattern across years
# ============================================================
print("\n=== Discovering RECURRING relationships ===")
recurring_count = 0

for (agency, base), group in by_sol_base.items():
    if len(group) < 2:
        continue
    group.sort(key=lambda o: o.year or 0)
    for i in range(len(group) - 1):
        add_rel(
            group[i].id, group[i+1].id,
            "recurring", 0.85,
            f"Same program family at {agency}: {base}",
            f"Sol: {group[i].solicitation_number} -> {group[i+1].solicitation_number}"
        )
        recurring_count += 1

# Also detect by similar names within same agency
for agency, agency_opps in by_agency.items():
    if len(agency_opps) < 2:
        continue
    
    # Normalize names for comparison
    name_groups = defaultdict(list)
    for o in agency_opps:
        name = o.name or ""
        # Remove year references, round numbers, version numbers
        norm = re.sub(r'\b20\d{2}\b', '', name)
        norm = re.sub(r'\b(Round|Phase|Cohort|Version|FY)\s*\d+\b', '', norm, flags=re.IGNORECASE)
        norm = re.sub(r'\s+', ' ', norm).strip().lower()
        if len(norm) > 15:  # Only meaningful names
            name_groups[norm].append(o)
    
    for norm_name, group in name_groups.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda o: o.year or 0)
        for i in range(len(group) - 1):
            if group[i].id != group[i+1].id:
                add_rel(
                    group[i].id, group[i+1].id,
                    "recurring", 0.80,
                    f"Similar program name at {agency}",
                    f"'{group[i].name}' -> '{group[i+1].name}'"
                )
                recurring_count += 1

print(f"  Found {recurring_count} recurring relationships")

# ============================================================
# 2. COMPLEMENTARY: Different agencies, same technology, overlapping time
# ============================================================
print("\n=== Discovering COMPLEMENTARY relationships ===")
complementary_count = 0

# For each technology keyword, find opportunities from different agencies in similar timeframes
SIGNIFICANT_TECHS = {
    "Solar", "Wind", "Energy Storage", "Hydrogen", "Nuclear",
    "Carbon Management", "Grid Modernization", "Clean Transportation",
    "Building Efficiency", "Bioenergy", "Geothermal", "Industrial",
    "Electrification", "Grid Cybersecurity",
}

for tech in SIGNIFICANT_TECHS:
    tech_opps = by_keyword.get(tech, [])
    if len(tech_opps) < 2:
        continue
    
    # Group by year ranges (3-year windows)
    for year_center in range(2012, 2027):
        window_opps = [o for o in tech_opps if o.year and abs(o.year - year_center) <= 1]
        if len(window_opps) < 2:
            continue
        
        # Find pairs from different agencies
        agencies_in_window = defaultdict(list)
        for o in window_opps:
            agencies_in_window[o.agency].append(o)
        
        agency_list = list(agencies_in_window.keys())
        if len(agency_list) < 2:
            continue
        
        # Connect representative opportunities across agencies (limit to avoid explosion)
        for a1, a2 in combinations(agency_list, 2):
            # Just link the first from each agency in this window
            o1 = agencies_in_window[a1][0]
            o2 = agencies_in_window[a2][0]
            add_rel(
                o1.id, o2.id,
                "complementary", 0.65,
                f"Both fund {tech} in {year_center-1}-{year_center+1}",
                f"{o1.agency}: {o1.name[:60]} | {o2.agency}: {o2.name[:60]}"
            )
            complementary_count += 1

print(f"  Found {complementary_count} complementary relationships")

# ============================================================
# 3. STACKABLE: State + federal programs in same tech area
# ============================================================
print("\n=== Discovering STACKABLE relationships ===")
stackable_count = 0

STATE_AGENCIES = {
    "NYSERDA", "CEC", "MassCEC", "WI OEI", "Efficiency Maine",
    "NM EMNRD", "MD MEA", "TX SECO", "NJEDA", "IL DCEO",
    "Colorado CEO", "WA Commerce", "MN Commerce",
}
FEDERAL_AGENCIES = {"DOE", "ARPA-E", "NSF", "EPA", "USDA", "DOC"}

state_opps = [o for o in opps if o.agency in STATE_AGENCIES and (not o.is_historical or o.status == "open")]
federal_opps = [o for o in opps if o.agency in FEDERAL_AGENCIES and (not o.is_historical or o.status == "open")]

for s_opp in state_opps:
    s_kw = getattr(s_opp, '_kw_set', set())
    if not s_kw:
        continue
    
    for f_opp in federal_opps:
        f_kw = getattr(f_opp, '_kw_set', set())
        if not f_kw:
            continue
        
        # Require at least 2 keyword overlaps for stackable
        overlap = s_kw & f_kw
        if len(overlap) >= 2:
            # Check time overlap (within 2 years or both current)
            s_yr = s_opp.year or 2026
            f_yr = f_opp.year or 2026
            if abs(s_yr - f_yr) <= 2:
                add_rel(
                    s_opp.id, f_opp.id,
                    "stackable", 0.60,
                    f"State+federal stack: {', '.join(sorted(overlap)[:3])}",
                    f"{s_opp.agency} + {f_opp.agency}"
                )
                stackable_count += 1
    
    # Cap to avoid explosion
    if stackable_count > 500:
        break

print(f"  Found {stackable_count} stackable relationships")

# ============================================================
# 4. SAME_PROGRAM_FAMILY: Shared CFDA numbers or program names
# ============================================================
print("\n=== Discovering SAME_PROGRAM_FAMILY relationships ===")
family_count = 0

# Group by agency_code (sub-agency) - opportunities from same sub-agency are family
for agency, agency_opps in by_agency.items():
    code_groups = defaultdict(list)
    for o in agency_opps:
        code = o.agency_code or ""
        if code:
            code_groups[code].append(o)
    
    for code, group in code_groups.items():
        if len(group) < 2 or len(group) > 50:  # Skip huge groups
            continue
        # Sort by year and connect sequential pairs
        group.sort(key=lambda o: o.year or 0)
        for i in range(len(group) - 1):
            # Only connect if they share at least 1 keyword
            kw1 = getattr(group[i], '_kw_set', set())
            kw2 = getattr(group[i+1], '_kw_set', set())
            if kw1 & kw2:
                add_rel(
                    group[i].id, group[i+1].id,
                    "same_program_family", 0.55,
                    f"Same sub-agency: {code}",
                    f"Shared topics: {', '.join(sorted((kw1 & kw2))[:3])}"
                )
                family_count += 1

print(f"  Found {family_count} program family relationships")

# ============================================================
# 5. TOPICAL_CLUSTER: High keyword overlap across organizations
# ============================================================
print("\n=== Discovering TOPICAL_CLUSTER relationships ===")
cluster_count = 0

# Find opportunities with 4+ shared keywords from different agencies
# Only do this for current/recent opportunities to keep it manageable
recent = [o for o in opps if (o.year or 0) >= 2023 and len(getattr(o, '_kw_set', set())) >= 3]

for i in range(len(recent)):
    for j in range(i + 1, min(i + 200, len(recent))):  # Limit comparisons
        o1, o2 = recent[i], recent[j]
        if o1.agency == o2.agency:
            continue  # Same agency covered by recurring
        
        overlap = o1._kw_set & o2._kw_set
        if len(overlap) >= 4:
            confidence = min(0.90, 0.50 + 0.10 * len(overlap))
            add_rel(
                o1.id, o2.id,
                "topical_cluster", confidence,
                f"High topic overlap ({len(overlap)} shared): {', '.join(sorted(overlap)[:4])}",
                f"{o1.agency} + {o2.agency}"
            )
            cluster_count += 1

print(f"  Found {cluster_count} topical cluster relationships")

# ============================================================
# SAVE ALL RELATIONSHIPS
# ============================================================
print(f"\n=== Saving {len(relationships)} total relationships ===")

batch_size = 500
for i in range(0, len(relationships), batch_size):
    batch = relationships[i:i+batch_size]
    db.add_all(batch)
    db.commit()
    print(f"  Saved batch {i//batch_size + 1} ({len(batch)} records)")

# Final counts
print("\n" + "=" * 60)
print("  RELATIONSHIP DISCOVERY COMPLETE")
print("=" * 60)

total_rels = db.execute(text("SELECT COUNT(*) FROM opportunity_relationships")).scalar()
type_counts = db.execute(text(
    "SELECT relationship_type, COUNT(*) FROM opportunity_relationships GROUP BY relationship_type ORDER BY COUNT(*) DESC"
)).fetchall()

print(f"  Total relationships: {total_rels}")
for rtype, cnt in type_counts:
    print(f"    {rtype:<25} {cnt:>5}")

# Show some example relationships
print("\n  Sample relationships:")
samples = db.execute(text("""
    SELECT r.relationship_type, r.confidence, r.rationale,
           s.agency as src_agency, s.name as src_name,
           t.agency as tgt_agency, t.name as tgt_name
    FROM opportunity_relationships r
    JOIN opportunities s ON r.source_opp_id = s.id
    JOIN opportunities t ON r.target_opp_id = t.id
    ORDER BY r.confidence DESC
    LIMIT 10
""")).fetchall()

for s in samples:
    print(f"    [{s[0]}] {s[1]:.0%} | {s[3]}: {s[4][:40]} <-> {s[5]}: {s[6][:40]}")
    print(f"      Reason: {s[2][:80]}")

print("=" * 60)
db.close()
