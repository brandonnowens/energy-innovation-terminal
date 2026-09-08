from app.database import SessionLocal
from sqlalchemy import text

def test():
    db = SessionLocal()
    is_pg = db.bind.dialect.name == "postgresql"
    agg_agency = "string_agg(DISTINCT a.agency, ', ')" if is_pg else "GROUP_CONCAT(DISTINCT a.agency)"
    agg_tech = "string_agg(DISTINCT oc.category_value, ', ')" if is_pg else "GROUP_CONCAT(DISTINCT oc.category_value)"

    print("Database dialect:", db.bind.dialect.name)

    # 1. Top agencies
    agency_stats = db.execute(text("""
        SELECT a.agency,
               COUNT(a.id) as award_count,
               COALESCE(SUM(a.award_amount), 0) as total_funding,
               COUNT(DISTINCT a.recipient_name) as unique_awardees,
               COUNT(DISTINCT a.program_name) as distinct_programs
        FROM awards a
        WHERE a.agency IS NOT NULL
        GROUP BY a.agency
        ORDER BY total_funding DESC
        LIMIT 10
    """)).fetchall()
    print("Top agencies:", [(r[0], r[1], f"${r[2]/1e6:.1f}M") for r in agency_stats[:3]])

    # 2. Bridge awardees
    bridge_sql = f"""
        SELECT a.recipient_name,
               COUNT(DISTINCT a.agency) as agency_count,
               {agg_agency} as agencies,
               COUNT(a.id) as award_count,
               COALESCE(SUM(a.award_amount), 0) as total_funding,
               a.recipient_city, a.recipient_state
        FROM awards a
        WHERE a.recipient_name IS NOT NULL AND a.agency IS NOT NULL
        GROUP BY a.recipient_name, a.recipient_city, a.recipient_state
        HAVING COUNT(DISTINCT a.agency) >= 2
        ORDER BY agency_count DESC, total_funding DESC
        LIMIT 20
    """
    bridge_rows = db.execute(text(bridge_sql)).fetchall()
    print("Bridge awardees count:", len(bridge_rows))
    if bridge_rows:
        print("Sample bridge:", bridge_rows[0][0], "| Agencies:", bridge_rows[0][1], f"| Funding: ${bridge_rows[0][4]/1e6:.2f}M")

    # 3. Tech hubs
    tech_sql = """
        SELECT oc.category_value,
               COUNT(DISTINCT oc.opportunity_id) as opp_count,
               COUNT(DISTINCT o.agency) as agency_count,
               COUNT(DISTINCT a.id) as award_count,
               COALESCE(SUM(a.award_amount), 0) as total_awarded
        FROM opportunity_categories oc
        JOIN opportunities o ON o.id = oc.opportunity_id
        LEFT JOIN awards a ON a.opportunity_id = o.id
        WHERE oc.category_type = 'technology' AND oc.category_value != '' AND oc.category_value NOT IN ('Unknown', 'Other')
        GROUP BY oc.category_value
        ORDER BY opp_count DESC
        LIMIT 20
    """
    tech_rows = db.execute(text(tech_sql)).fetchall()
    print("Tech hubs count:", len(tech_rows))
    if tech_rows:
        print("Top tech:", tech_rows[0][0], "| Opps:", tech_rows[0][1], "| Agencies:", tech_rows[0][2], f"| Awarded: ${tech_rows[0][4]/1e6:.2f}M")

    # 4. Cross agency synergies
    agg_syn = "string_agg(DISTINCT at1.category_value, ', ')" if is_pg else "GROUP_CONCAT(DISTINCT at1.category_value)"
    syn_sql = f"""
        WITH agency_techs AS (
            SELECT DISTINCT o.agency, oc.category_value
            FROM opportunity_categories oc
            JOIN opportunities o ON o.id = oc.opportunity_id
            WHERE oc.category_type = 'technology'
              AND o.agency IS NOT NULL
              AND oc.category_value != '' AND oc.category_value NOT IN ('Unknown', 'Other')
        )
        SELECT at1.agency as agency_a,
               at2.agency as agency_b,
               COUNT(at1.category_value) as shared_tech_count,
               {agg_syn} as shared_techs
        FROM agency_techs at1
        JOIN agency_techs at2 ON at1.category_value = at2.category_value AND at1.agency < at2.agency
        GROUP BY at1.agency, at2.agency
        HAVING COUNT(at1.category_value) >= 2
        ORDER BY shared_tech_count DESC
        LIMIT 15
    """
    syn_rows = db.execute(text(syn_sql)).fetchall()
    print("Synergies count:", len(syn_rows))
    if syn_rows:
        print("Sample synergy:", syn_rows[0][0], "&", syn_rows[0][1], "| Shared techs:", syn_rows[0][2], "| Examples:", syn_rows[0][3][:80])

    db.close()

if __name__ == "__main__":
    test()
