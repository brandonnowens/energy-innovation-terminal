import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import re
from collections import Counter, defaultdict

conn = engine.connect()
c = conn.cursor()

print("=" * 80)
print("DEEP AUDIT: LINKAGES, TAXONOMIES, CATEGORIES, & FALSE PRECISION")
print("=" * 80)

# 1. Awards -> Opportunity Linkage
total_awards = c.execute(text("SELECT COUNT(*) FROM awards")).fetchone()[0]
linked_awards = c.execute(text("SELECT COUNT(*) FROM awards WHERE opportunity_id IS NOT NULL")).fetchone()[0]
print(f"\n1. AWARDS -> OPPORTUNITY LINKAGES:")
print(f"   Total Awards: {total_awards:,}")
print(f"   Awards with opportunity_id: {linked_awards:,} ({linked_awards/total_awards*100:.1f}%)")

# Check distinct opportunity_ids in awards
distinct_opps_in_awards = c.execute(text("SELECT COUNT(DISTINCT opportunity_id) FROM awards WHERE opportunity_id IS NOT NULL")).fetchone()[0]
print(f"   Distinct opportunities linked to awards: {distinct_opps_in_awards:,}")

# Sample award to opportunity linkages
print("\n   Sample Award-to-Opportunity mappings:")
for r in c.execute(text("SELECT a.id, a.agency, a.award_amount, a.recipient_name, a.project_title, o.id, o.solicitation_number, o.name FROM awards a JOIN opportunities o ON a.opportunity_id = o.id LIMIT 5")):
    print(f"   Award #{r[0]} [{r[1]}]: '{r[3]}' (${r[2]:,.0f} on '{r[4][:40]}...') -> Opp #{r[5]} [{r[6]}]: '{r[7][:40]}...'")

# 2. Opportunity Categories Analysis
print("\n" + "=" * 80)
print("2. OPPORTUNITY CATEGORIES CANONICAL DISTRIBUTION:")
print("=" * 80)

for cat_type in ['technology', 'sector', 'fuel', 'fuel_type', 'activity']:
    rows = c.execute("SELECT category_value, COUNT(*), COUNT(DISTINCT opportunity_id) FROM opportunity_categories WHERE category_type=? GROUP BY category_value ORDER BY COUNT(*) DESC", (cat_type,)).fetchall()
    print(f"\nCategory Type: '{cat_type}' ({len(rows)} distinct values):")
    for val, total_cnt, opp_cnt in rows[:20]:
        print(f"   {val:<38} Occurrences: {total_cnt:<6} Opps: {opp_cnt:<6}")

# 3. Check for Tag Overlap / Inflation per Opportunity
print("\n" + "=" * 80)
print("3. CATEGORY INFLATION & MULTI-TAGGING AUDIT:")
print("=" * 80)

for cat_type in ['technology', 'sector', 'fuel', 'activity']:
    opp_tag_counts = c.execute(f"SELECT opportunity_id, COUNT(*) FROM opportunity_categories WHERE category_type='{cat_type}' GROUP BY opportunity_id").fetchall()
    counts = [cnt for _, cnt in opp_tag_counts]
    if counts:
        avg_cnt = sum(counts) / len(counts)
        max_cnt = max(counts)
        counter = Counter(counts)
        print(f"\n{cat_type.upper()} Tags per Opportunity:")
        print(f"   Avg: {avg_cnt:.2f} tags/opp | Max: {max_cnt} tags/opp")
        print(f"   Distribution: {dict(sorted(counter.items())[:10])}")

# 4. Check for Suspicious / Low-Precision Matches
print("\n" + "=" * 80)
print("4. SUSPICIOUS / OVER-MATCHED OPPORTUNITIES:")
print("=" * 80)

# Check opportunities with > 5 technologies
over_tagged = c.execute(text("SELECT o.id, o.agency, o.solicitation_number, o.name, COUNT(oc.id) as tag_cnt FROM opportunities o JOIN opportunity_categories oc ON o.id = oc.opportunity_id WHERE oc.category_type='technology' GROUP BY o.id HAVING tag_cnt > 5 ORDER BY tag_cnt DESC LIMIT 8")).fetchall()
print(f"Opportunities with >5 technology tags (potential over-inference): {len(over_tagged)}")
for r in over_tagged:
    techs = [t[0] for t in c.execute("SELECT category_value FROM opportunity_categories WHERE opportunity_id=? AND category_type='technology'", (r[0],)).fetchall()]
    print(f"   Opp #{r[0]} [{r[1]} - {r[2]}]: '{r[3][:50]}...' -> {r[4]} techs: {techs}")

# 5. Check Inconsistencies / Redundancies
print("\n" + "=" * 80)
print("5. CANONICAL TAXONOMY REDUNDANCY AUDIT:")
print("=" * 80)
# Look for duplicates like 'Electric Vehicles' vs 'Electric Vehicles & Clean Transit'
all_techs = [r[0] for r in c.execute(text("SELECT DISTINCT category_value FROM opportunity_categories WHERE category_type='technology'")).fetchall()]
print(f"Total distinct technology values: {len(all_techs)}")
print(f"All technology values: {sorted(all_techs)}")

all_sectors = [r[0] for r in c.execute(text("SELECT DISTINCT category_value FROM opportunity_categories WHERE category_type='sector'")).fetchall()]
print(f"\nTotal distinct sector values: {len(all_sectors)}")
print(f"All sector values: {sorted(all_sectors)}")

all_fuels = [r[0] for r in c.execute(text("SELECT DISTINCT category_value FROM opportunity_categories WHERE category_type IN ('fuel', 'fuel_type')")).fetchall()]
print(f"\nTotal distinct fuel values: {len(all_fuels)}")
print(f"All fuel values: {sorted(all_fuels)}")

conn.close()
