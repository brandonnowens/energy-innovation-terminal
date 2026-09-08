from app.database import SessionLocal
from sqlalchemy import text

def test():
    db = SessionLocal()
    is_pg = db.bind.dialect.name == "postgresql"
    agg_agency = "string_agg(DISTINCT o.agency, ', ')" if is_pg else "GROUP_CONCAT(DISTINCT o.agency)"

    print("=== TRENDS ANALYTICS TEST ===")
    yearly = db.execute(text("""
        SELECT year, COUNT(id) as count, COALESCE(SUM(total_funding), 0) as total_funding
        FROM opportunities
        WHERE year >= 2018 AND year <= 2026
        GROUP BY year
        ORDER BY year
    """)).fetchall()
    print("Yearly summary (2018-2026):", [(r[0], r[1], f"${r[2]/1e6:.1f}M") for r in yearly])

    tech_growth = db.execute(text("""
        SELECT oc.category_value,
               COUNT(CASE WHEN o.year >= 2022 THEN 1 END) as recent_count,
               COUNT(CASE WHEN o.year < 2022 AND o.year >= 2018 THEN 1 END) as prior_count,
               COALESCE(SUM(CASE WHEN o.year >= 2022 THEN o.total_funding ELSE 0 END), 0) as recent_funding
        FROM opportunity_categories oc
        JOIN opportunities o ON o.id = oc.opportunity_id
        WHERE oc.category_type = 'technology' AND oc.category_value != '' AND oc.category_value NOT IN ('Unknown', 'Other')
        GROUP BY oc.category_value
        HAVING COUNT(CASE WHEN o.year >= 2022 THEN 1 END) >= 5
        ORDER BY recent_funding DESC
        LIMIT 10
    """)).fetchall()
    print("Top recent tech:", [(r[0], r[1], f"${r[3]/1e6:.1f}M") for r in tech_growth[:4]])

    print("\n=== SANKEY ANALYTICS TEST ===")
    conduits = db.execute(text("""
        SELECT o.agency,
               COALESCE(cs.category_value, 'Power & Grid') as sector,
               COALESCE(ct.category_value, 'Clean Energy') as technology,
               SUM(COALESCE(o.total_funding, 0)) as total_funding,
               COUNT(DISTINCT o.id) as opp_count
        FROM opportunities o
        LEFT JOIN opportunity_categories cs ON o.id = cs.opportunity_id AND cs.category_type = 'sector'
        LEFT JOIN opportunity_categories ct ON o.id = ct.opportunity_id AND ct.category_type = 'technology'
        WHERE o.agency IS NOT NULL AND cs.category_value NOT IN ('Unknown', 'Other') AND ct.category_value NOT IN ('Unknown', 'Other')
        GROUP BY o.agency, cs.category_value, ct.category_value
        ORDER BY total_funding DESC
        LIMIT 6
    """)).fetchall()
    print("Macro Conduits:", [(r[0], r[1], r[2], f"${r[3]/1e6:.1f}M", r[4]) for r in conduits[:4]])

    tech_div = db.execute(text(f"""
        SELECT ct.category_value as technology,
               COUNT(DISTINCT o.agency) as agency_count,
               {agg_agency} as agencies,
               COUNT(DISTINCT o.id) as opp_count,
               SUM(COALESCE(o.total_funding, 0)) as total_funding
        FROM opportunity_categories ct
        JOIN opportunities o ON ct.opportunity_id = o.id
        WHERE ct.category_type = 'technology' AND ct.category_value != '' AND ct.category_value NOT IN ('Unknown', 'Other')
        GROUP BY ct.category_value
        HAVING COUNT(DISTINCT o.agency) >= 5
        ORDER BY total_funding DESC
        LIMIT 6
    """)).fetchall()
    print("Multi-agency tech:", [(r[0], r[1], f"${r[4]/1e6:.1f}M", r[2][:60]) for r in tech_div[:4]])

    db.close()

if __name__ == "__main__":
    test()
