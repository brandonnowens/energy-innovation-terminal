import psycopg2

db_url = "postgresql://postgres.muihufwteznnncvwqovz:AtWkDzYsICn5axnw@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"

views_sql = {
    # 1. Executive Database Summary KPIs
    "vw_database_summary_kpis": """
    CREATE OR REPLACE VIEW vw_database_summary_kpis AS
    SELECT 
        (SELECT COUNT(*) FROM opportunities) AS total_opportunities,
        (SELECT COUNT(*) FROM opportunities WHERE status = 'open') AS active_open_opportunities,
        (SELECT COALESCE(SUM(total_funding), 0) FROM opportunities) AS total_pipeline_funding_usd,
        (SELECT COUNT(*) FROM awards) AS total_awards_count,
        (SELECT COALESCE(SUM(award_amount), 0) FROM awards) AS total_awarded_usd,
        (SELECT COUNT(*) FROM recipients) AS total_unique_recipients,
        (SELECT COUNT(*) FROM organizations) AS total_organizations,
        (SELECT COUNT(*) FROM programs WHERE active = true) AS total_structured_programs,
        (SELECT COUNT(*) FROM technologies) AS total_technologies_tracked,
        (SELECT COUNT(*) FROM recipient_patents) AS total_patents_tracked,
        (SELECT COALESCE(SUM(amount_usd), 0) FROM recipient_investments) AS total_vc_investments_usd,
        (SELECT COALESCE(SUM(total_amount_sold_usd), 0) FROM sec_form_d_filings) AS total_sec_form_d_sold_usd,
        (SELECT COUNT(*) FROM policy_standards) AS total_policy_standards;
    """,

    # 2. Agency Portfolios Summary
    "vw_agency_portfolios_summary": """
    CREATE OR REPLACE VIEW vw_agency_portfolios_summary AS
    WITH opp_agg AS (
        SELECT 
            COALESCE(agency, 'Unknown') AS agency_name,
            COUNT(*) AS total_solicitations,
            COUNT(*) FILTER (WHERE status = 'open') AS active_solicitations,
            COALESCE(SUM(total_funding), 0) AS total_pipeline_funding_usd
        FROM opportunities
        GROUP BY agency
    ),
    award_agg AS (
        SELECT 
            COALESCE(agency, 'Unknown') AS agency_name,
            COUNT(DISTINCT id) AS total_awards,
            COALESCE(SUM(award_amount), 0) AS total_awarded_usd,
            COUNT(DISTINCT recipient_name) AS unique_recipients,
            MIN(year) AS first_award_year,
            MAX(year) AS latest_award_year
        FROM awards
        GROUP BY agency
    )
    SELECT 
        COALESCE(o.name, opp.agency_name, aw.agency_name) AS organization_name,
        o.org_type,
        o.geographic_scope,
        o.state,
        COALESCE(opp.total_solicitations, 0) AS total_solicitations,
        COALESCE(opp.active_solicitations, 0) AS active_solicitations,
        COALESCE(opp.total_pipeline_funding_usd, 0) AS total_pipeline_funding_usd,
        COALESCE(aw.total_awards, 0) AS total_awards,
        COALESCE(aw.total_awarded_usd, 0) AS total_awarded_usd,
        COALESCE(aw.unique_recipients, 0) AS unique_recipients,
        aw.first_award_year,
        aw.latest_award_year
    FROM opp_agg opp
    FULL OUTER JOIN award_agg aw ON aw.agency_name = opp.agency_name
    LEFT JOIN organizations o ON LOWER(o.name) = LOWER(COALESCE(opp.agency_name, aw.agency_name))
    ORDER BY total_awarded_usd DESC, total_pipeline_funding_usd DESC;
    """,

    # 3. Program Initiatives Summary
    "vw_program_initiatives_summary": """
    CREATE OR REPLACE VIEW vw_program_initiatives_summary AS
    WITH opp_p AS (
        SELECT 
            program_id,
            COUNT(*) AS total_opportunities,
            COUNT(*) FILTER (WHERE status = 'open') AS active_opportunities,
            COALESCE(SUM(total_funding), 0) AS total_program_funding_usd
        FROM opportunities
        WHERE program_id IS NOT NULL
        GROUP BY program_id
    ),
    aw_p AS (
        SELECT 
            o.program_id,
            COUNT(DISTINCT a.id) AS award_count,
            COALESCE(SUM(a.award_amount), 0) AS total_awarded_usd
        FROM awards a
        JOIN opportunities o ON o.id = a.opportunity_id
        WHERE o.program_id IS NOT NULL
        GROUP BY o.program_id
    ),
    fa_p AS (
        SELECT 
            program_id,
            STRING_AGG(focus_area, ', ') AS focus_areas_list
        FROM program_focus_areas
        GROUP BY program_id
    )
    SELECT 
        p.id AS program_id,
        p.name AS program_name,
        p.program_type,
        p.parent_program,
        p.target_stage,
        p.target_applicant,
        p.active AS is_active,
        COALESCE(op.total_opportunities, 0) AS total_opportunities_count,
        COALESCE(op.active_opportunities, 0) AS active_opportunities_count,
        COALESCE(op.total_program_funding_usd, 0) AS total_program_funding_usd,
        COALESCE(aw.award_count, 0) AS award_count,
        COALESCE(aw.total_awarded_usd, 0) AS total_awarded_usd,
        fa.focus_areas_list,
        p.url AS official_url
    FROM programs p
    LEFT JOIN opp_p op ON op.program_id = p.id
    LEFT JOIN aw_p aw ON aw.program_id = p.id
    LEFT JOIN fa_p fa ON fa.program_id = p.id
    ORDER BY total_program_funding_usd DESC, total_awarded_usd DESC;
    """,

    # 4. Active Solicitations Dossier
    "vw_active_solicitations_dossier": """
    CREATE OR REPLACE VIEW vw_active_solicitations_dossier AS
    SELECT 
        o.id AS opportunity_id,
        o.name AS opportunity_name,
        o.agency,
        o.solicitation_number,
        p.name AS program_name,
        p.program_type,
        o.status,
        o.total_funding AS total_funding_usd,
        o.max_per_award AS max_per_award_usd,
        o.award_min AS min_per_award_usd,
        o.cost_share_mandatory,
        o.cost_share_pct,
        o.close_date,
        CASE 
            WHEN o.close_date IS NOT NULL THEN (o.close_date::date - CURRENT_DATE)
            ELSE NULL 
        END AS days_until_close,
        o.eligible_applicant_types,
        o.eligible_technology_areas,
        o.eligible_sectors,
        o.jurisdiction,
        o.geographic_scope,
        COALESCE(o.portal_url, o.detail_page_url, o.source_url) AS portal_url
    FROM opportunities o
    LEFT JOIN programs p ON p.id = o.program_id
    WHERE o.status = 'open'
    ORDER BY o.close_date ASC NULLS LAST, o.total_funding DESC;
    """,

    # 5. Top Recipients Leaderboard
    "vw_top_recipients_leaderboard": """
    CREATE OR REPLACE VIEW vw_top_recipients_leaderboard AS
    WITH vc_rec AS (
        SELECT 
            recipient_id,
            COUNT(*) AS vc_rounds_count,
            COALESCE(SUM(amount_usd), 0) AS total_vc_funding_usd
        FROM recipient_investments
        GROUP BY recipient_id
    ),
    pat_rec AS (
        SELECT 
            recipient_id,
            COUNT(*) AS total_patents_count
        FROM recipient_patents
        GROUP BY recipient_id
    ),
    sec_rec AS (
        SELECT 
            recipient_id,
            COALESCE(SUM(total_amount_sold_usd), 0) AS total_sec_sold_usd
        FROM sec_form_d_filings
        GROUP BY recipient_id
    )
    SELECT 
        r.id AS recipient_id,
        r.name AS recipient_name,
        r.recipient_type,
        r.headquarters_city,
        r.headquarters_state,
        r.is_ny_based,
        r.primary_technology,
        COALESCE(r.total_awards_count, 0) AS public_awards_count,
        COALESCE(r.total_funding_received, 0) AS public_grant_funding_usd,
        COALESCE(vc.total_vc_funding_usd, 0) AS private_vc_funding_usd,
        COALESCE(sec.total_sec_sold_usd, 0) AS sec_form_d_sold_usd,
        (COALESCE(r.total_funding_received, 0) + COALESCE(vc.total_vc_funding_usd, 0) + COALESCE(sec.total_sec_sold_usd, 0)) AS total_capital_volume_usd,
        COALESCE(pat.total_patents_count, 0) AS patents_count,
        r.funded_agencies,
        r.first_award_year,
        r.latest_award_year,
        r.website_url
    FROM recipients r
    LEFT JOIN vc_rec vc ON vc.recipient_id = r.id
    LEFT JOIN pat_rec pat ON pat.recipient_id = r.id
    LEFT JOIN sec_rec sec ON sec.recipient_id = r.id
    ORDER BY total_capital_volume_usd DESC, public_grant_funding_usd DESC;
    """,

    # 6. Technology Sector Capital Flows
    "vw_technology_sector_capital_flows": """
    CREATE OR REPLACE VIEW vw_technology_sector_capital_flows AS
    WITH cat_opp AS (
        SELECT 
            c.category_value AS tech_keyword,
            COUNT(DISTINCT c.opportunity_id) AS tagged_opportunities,
            COUNT(DISTINCT c.opportunity_id) FILTER (WHERE o.status = 'open') AS active_opportunities,
            COALESCE(SUM(o.total_funding), 0) AS pipeline_funding_usd
        FROM opportunity_categories c
        JOIN opportunities o ON o.id = c.opportunity_id
        WHERE c.category_type = 'technology'
        GROUP BY c.category_value
    )
    SELECT 
        t.id AS tech_id,
        t.name AS technology_name,
        t.sector,
        t.vector_type,
        t.fuel_vector,
        t.trl_current,
        t.trl_target,
        COALESCE(co.tagged_opportunities, 0) AS tagged_opportunities_count,
        COALESCE(co.active_opportunities, 0) AS active_opportunities_count,
        COALESCE(co.pipeline_funding_usd, 0) AS total_pipeline_funding_usd,
        t.headline
    FROM technologies t
    LEFT JOIN cat_opp co ON LOWER(co.tech_keyword) = LOWER(t.name) OR LOWER(co.tech_keyword) = LOWER(t.id)
    ORDER BY total_pipeline_funding_usd DESC, tagged_opportunities_count DESC;
    """,

    # 7. State Geographic Funding Summary
    "vw_state_geographic_funding_summary": """
    CREATE OR REPLACE VIEW vw_state_geographic_funding_summary AS
    WITH state_awards AS (
        SELECT 
            COALESCE(recipient_state, 'Unknown') AS state_code,
            COUNT(*) AS total_awards_count,
            COALESCE(SUM(award_amount), 0) AS total_awarded_usd,
            COUNT(DISTINCT recipient_name) AS unique_recipients_count
        FROM awards
        WHERE recipient_state IS NOT NULL AND recipient_state != ''
        GROUP BY recipient_state
    ),
    state_recipients AS (
        SELECT 
            headquarters_state AS state_code,
            COUNT(*) AS total_recipients_count,
            COALESCE(SUM(total_funding_received), 0) AS recipient_total_funding_usd
        FROM recipients
        WHERE headquarters_state IS NOT NULL AND headquarters_state != ''
        GROUP BY headquarters_state
    )
    SELECT 
        COALESCE(sa.state_code, sr.state_code) AS state_code,
        COALESCE(sa.total_awards_count, 0) AS total_awards_count,
        COALESCE(sa.total_awarded_usd, 0) AS total_awarded_usd,
        COALESCE(sa.unique_recipients_count, 0) AS unique_awardees_count,
        COALESCE(sr.total_recipients_count, 0) AS total_headquartered_recipients_count,
        COALESCE(sr.recipient_total_funding_usd, 0) AS recipient_total_funding_usd
    FROM state_awards sa
    FULL OUTER JOIN state_recipients sr ON sr.state_code = sa.state_code
    WHERE COALESCE(sa.state_code, sr.state_code) NOT IN ('Unknown', '')
    ORDER BY total_awarded_usd DESC, total_awards_count DESC;
    """,

    # 8. Capital Stack Hybrid Intelligence
    "vw_capital_stack_hybrid_intelligence": """
    CREATE OR REPLACE VIEW vw_capital_stack_hybrid_intelligence AS
    SELECT 
        r.id AS recipient_id,
        r.name AS company_name,
        r.headquarters_state AS state,
        r.recipient_type,
        r.primary_technology,
        COALESCE(r.total_funding_received, 0) AS public_grants_usd,
        COALESCE(r.total_awards_count, 0) AS public_awards_count,
        COALESCE((SELECT SUM(amount_usd) FROM recipient_investments WHERE recipient_id = r.id), 0) AS private_vc_usd,
        (SELECT COUNT(*) FROM recipient_investments WHERE recipient_id = r.id) AS vc_rounds_count,
        (SELECT round_type FROM recipient_investments WHERE recipient_id = r.id ORDER BY round_date DESC NULLS LAST LIMIT 1) AS latest_vc_round_type,
        (SELECT lead_investor FROM recipient_investments WHERE recipient_id = r.id ORDER BY round_date DESC NULLS LAST LIMIT 1) AS latest_vc_lead_investor,
        COALESCE((SELECT SUM(total_amount_sold_usd) FROM sec_form_d_filings WHERE recipient_id = r.id), 0) AS sec_form_d_equity_usd,
        (SELECT COUNT(*) FROM recipient_patents WHERE recipient_id = r.id) AS patents_count,
        (COALESCE(r.total_funding_received, 0) + 
         COALESCE((SELECT SUM(amount_usd) FROM recipient_investments WHERE recipient_id = r.id), 0) + 
         COALESCE((SELECT SUM(total_amount_sold_usd) FROM sec_form_d_filings WHERE recipient_id = r.id), 0)) AS total_hybrid_capital_raised_usd
    FROM recipients r
    WHERE r.total_funding_received > 0 
       OR EXISTS (SELECT 1 FROM recipient_investments WHERE recipient_id = r.id)
       OR EXISTS (SELECT 1 FROM sec_form_d_filings WHERE recipient_id = r.id)
    ORDER BY total_hybrid_capital_raised_usd DESC;
    """,

    # 9. Policy & Statutory Mandates Matrix
    "vw_policy_statutory_mandates_matrix": """
    CREATE OR REPLACE VIEW vw_policy_statutory_mandates_matrix AS
    WITH pol_opp AS (
        SELECT 
            l.policy_id,
            COUNT(DISTINCT l.opportunity_id) AS linked_opportunities_count,
            COUNT(DISTINCT l.opportunity_id) FILTER (WHERE o.status = 'open') AS active_linked_opportunities_count,
            COALESCE(SUM(o.total_funding), 0) AS total_linked_pipeline_funding_usd
        FROM policy_opportunity_links l
        JOIN opportunities o ON o.id = l.opportunity_id
        GROUP BY l.policy_id
    )
    SELECT 
        p.id AS policy_id,
        p.code_identifier,
        p.short_title,
        p.title AS full_title,
        p.category,
        p.jurisdiction_level,
        p.jurisdiction_state,
        p.status,
        p.effective_year,
        p.sunset_year,
        COALESCE(po.linked_opportunities_count, 0) AS linked_opportunities_count,
        COALESCE(po.active_linked_opportunities_count, 0) AS active_linked_opportunities_count,
        COALESCE(po.total_linked_pipeline_funding_usd, 0) AS total_linked_pipeline_funding_usd,
        p.compliance_mandate,
        p.official_source_url
    FROM policy_standards p
    LEFT JOIN pol_opp po ON po.policy_id = p.id
    ORDER BY active_linked_opportunities_count DESC, linked_opportunities_count DESC;
    """
}

conn = psycopg2.connect(db_url)
cur = conn.cursor()

for name, query in views_sql.items():
    try:
        cur.execute(query)
        print(f"Created: {name}")
    except Exception as e:
        print(f"FAILED {name}: {e}")
        conn.rollback()

conn.commit()

print("\n--- Verifying View Queries ---")
for name in views_sql.keys():
    try:
        cur.execute(f"SELECT COUNT(*) FROM {name};")
        row_cnt = cur.fetchone()[0]
        print(f"OK: {name:40s} -> {row_cnt:>6,} rows")
    except Exception as e:
        print(f"ERROR querying {name}: {e}")
        conn.rollback()

cur.close()
conn.close()
