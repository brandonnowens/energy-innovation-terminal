import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import json
from collections import Counter

conn = engine.connect()
c = conn.cursor()

print("=" * 80)
print("COMPREHENSIVE TAXONOMY & CLASSIFICATION AUDIT")
print("=" * 80)

# 1. Inspect table schemas
tables = [r[0] for r in c.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()]
print(f"Tables in database: {tables}\n")

# Check opportunity_categories
print("--- OPPORTUNITY CATEGORIES ---")
op_cats = c.execute(text("SELECT category_type, COUNT(*), COUNT(DISTINCT opportunity_id), COUNT(DISTINCT category_value) FROM opportunity_categories GROUP BY category_type")).fetchall()
for t, cnt, opps, vals in op_cats:
    print(f"Type: {t:<15} Total records: {cnt:<8} Distinct opps: {opps:<8} Distinct values: {vals:<5}")

# Top values per category_type
for t, _, _, _ in op_cats:
    print(f"\nTop 10 values for category_type='{t}':")
    top_vals = c.execute("SELECT category_value, COUNT(*) as c, COUNT(DISTINCT opportunity_id) FROM opportunity_categories WHERE category_type=? GROUP BY category_value ORDER BY c DESC LIMIT 10", (t,)).fetchall()
    for val, cnt, opps in top_vals:
        print(f"   {val:<35} Total: {cnt:<6} Opps: {opps}")

# 2. Check Awards classification columns
print("\n" + "=" * 80)
print("--- AWARDS CLASSIFICATION COLUMNS ---")
award_cols = [r[1] for r in c.execute(text("PRAGMA table_info(awards)")).fetchall()]
print(f"Awards columns: {award_cols}")

# Check which classification columns exist on awards table
for col in ['technology', 'sector', 'fuel', 'stage', 'category', 'program_name', 'topic_name', 'award_type']:
    if col in award_cols:
        filled = c.execute(f"SELECT COUNT(*) FROM awards WHERE {col} IS NOT NULL AND {col} != ''").fetchone()[0]
        distinct = c.execute(f"SELECT COUNT(DISTINCT {col}) FROM awards WHERE {col} IS NOT NULL AND {col} != ''").fetchone()[0]
        print(f"Column '{col}': {filled:,} filled ({filled/54305*100:.1f}%), {distinct} distinct values")
        top_v = c.execute(f"SELECT {col}, COUNT(*), SUM(award_amount) FROM awards WHERE {col} IS NOT NULL AND {col} != '' GROUP BY {col} ORDER BY COUNT(*) DESC LIMIT 8").fetchall()
        for v, cnt, amt in top_v:
            amt_str = f"${amt/1e6:.1f}M" if amt else "$0"
            print(f"   - {str(v):<35} Count: {cnt:<7} Amount: {amt_str}")

# Check if there is an award_categories table or similar
if 'award_categories' in tables:
    print("\n--- AWARD CATEGORIES TABLE ---")
    ac_types = c.execute(text("SELECT category_type, COUNT(*), COUNT(DISTINCT award_id) FROM award_categories GROUP BY category_type")).fetchall()
    for t, cnt, awds in ac_types:
        print(f"Type: {t}: {cnt} rows across {awds} awards")

conn.close()
