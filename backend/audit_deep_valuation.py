import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import json
import os

def run_full_database_audit():
    conn = engine.connect()
    report = {}

    # 1. Tables & Row counts
    tables = [r[0] for r in conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")).fetchall()]
    table_counts = {}
    for t in tables:
        try:
            cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
            table_counts[t] = cnt
        except Exception as e:
            table_counts[t] = str(e)
    report['table_counts'] = table_counts


    # 2. Opportunities Analytics
    total_opps = cur.execute(text("SELECT COUNT(*) FROM opportunities")).fetchone()[0]
    opps_by_agency = cur.execute("""
        SELECT COALESCE(agency, 'UNKNOWN') as ag, COUNT(*) as cnt,
               SUM(CASE WHEN total_funding > 0 THEN 1 ELSE 0 END) as with_funding,
               SUM(COALESCE(total_funding, 0)) as sum_funding,
               AVG(CASE WHEN total_funding > 0 THEN total_funding ELSE NULL END) as avg_funding
        FROM opportunities
        GROUP BY ag
        ORDER BY cnt DESC
    """).fetchall()
    
    opps_by_status = cur.execute("""
        SELECT COALESCE(status, 'UNKNOWN') as st, COUNT(*) as cnt
        FROM opportunities
        GROUP BY st
        ORDER BY cnt DESC
    """).fetchall()

    opp_completeness = cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN name IS NOT NULL AND TRIM(name) != '' THEN 1 ELSE 0 END) as has_name,
            SUM(CASE WHEN short_description IS NOT NULL AND TRIM(short_description) != '' THEN 1 ELSE 0 END) as has_desc,
            SUM(CASE WHEN total_funding IS NOT NULL AND total_funding > 0 THEN 1 ELSE 0 END) as has_funding,
            SUM(CASE WHEN max_per_award IS NOT NULL AND max_per_award > 0 THEN 1 ELSE 0 END) as has_max_award,
            SUM(CASE WHEN open_date IS NOT NULL THEN 1 ELSE 0 END) as has_open_date,
            SUM(CASE WHEN close_date IS NOT NULL THEN 1 ELSE 0 END) as has_close_date,
            SUM(CASE WHEN detail_page_url IS NOT NULL OR source_url IS NOT NULL THEN 1 ELSE 0 END) as has_url,
            SUM(CASE WHEN target_trl_min IS NOT NULL OR target_trl_max IS NOT NULL THEN 1 ELSE 0 END) as has_trl,
            SUM(CASE WHEN geographic_scope IS NOT NULL AND TRIM(geographic_scope) != '' THEN 1 ELSE 0 END) as has_geo_scope,
            SUM(CASE WHEN program_id IS NOT NULL THEN 1 ELSE 0 END) as has_program,
            SUM(CASE WHEN organization_id IS NOT NULL THEN 1 ELSE 0 END) as has_org
        FROM opportunities
    """).fetchone()

    opp_dates = cur.execute("""
        SELECT 
            MIN(open_date) as min_open, MAX(open_date) as max_open,
            MIN(close_date) as min_close, MAX(close_date) as max_close,
            MIN(year) as min_year, MAX(year) as max_year
        FROM opportunities
    """).fetchone()

    report['opportunities'] = {
        'total': total_opps,
        'by_agency': [{k: r[k] for k in r.keys()} for r in opps_by_agency],
        'by_status': [{k: r[k] for k in r.keys()} for r in opps_by_status],
        'completeness': {k: opp_completeness[k] for k in opp_completeness.keys()},
        'date_range': {k: opp_dates[k] for k in opp_dates.keys()},
        'total_funding_tracked': sum([r['sum_funding'] for r in opps_by_agency])
    }

    # 3. Awards Analytics
    total_awards = cur.execute(text("SELECT COUNT(*) FROM awards")).fetchone()[0]
    awards_by_agency = cur.execute("""
        SELECT COALESCE(agency, 'UNKNOWN') as ag, COUNT(*) as cnt,
               SUM(CASE WHEN award_amount > 0 THEN 1 ELSE 0 END) as with_amount,
               SUM(COALESCE(award_amount, 0)) as sum_amount,
               AVG(CASE WHEN award_amount > 0 THEN award_amount ELSE NULL END) as avg_amount
        FROM awards
        GROUP BY ag
        ORDER BY cnt DESC
    """).fetchall()

    award_completeness = cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN recipient_name IS NOT NULL AND TRIM(recipient_name) != '' THEN 1 ELSE 0 END) as has_recipient,
            SUM(CASE WHEN award_amount IS NOT NULL AND award_amount > 0 THEN 1 ELSE 0 END) as has_amount,
            SUM(CASE WHEN award_date IS NOT NULL THEN 1 ELSE 0 END) as has_date,
            SUM(CASE WHEN project_title IS NOT NULL AND TRIM(project_title) != '' THEN 1 ELSE 0 END) as has_title,
            SUM(CASE WHEN project_abstract IS NOT NULL AND TRIM(project_abstract) != '' THEN 1 ELSE 0 END) as has_abstract,
            SUM(CASE WHEN recipient_state IS NOT NULL AND TRIM(recipient_state) != '' THEN 1 ELSE 0 END) as has_state,
            SUM(CASE WHEN recipient_city IS NOT NULL AND TRIM(recipient_city) != '' THEN 1 ELSE 0 END) as has_city,
            SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as has_lat_lng,
            SUM(CASE WHEN opportunity_id IS NOT NULL THEN 1 ELSE 0 END) as has_opp_link,
            SUM(CASE WHEN pi_name IS NOT NULL AND TRIM(pi_name) != '' THEN 1 ELSE 0 END) as has_pi_name,
            SUM(CASE WHEN pi_email IS NOT NULL AND TRIM(pi_email) != '' THEN 1 ELSE 0 END) as has_pi_email,
            SUM(CASE WHEN recipient_uei IS NOT NULL AND TRIM(recipient_uei) != '' THEN 1 ELSE 0 END) as has_uei,
            SUM(CASE WHEN recipient_website IS NOT NULL AND TRIM(recipient_website) != '' THEN 1 ELSE 0 END) as has_website
        FROM awards
    """).fetchone()

    award_dates = cur.execute("""
        SELECT MIN(award_date) as min_date, MAX(award_date) as max_date,
               MIN(year) as min_year, MAX(year) as max_year
        FROM awards
    """).fetchone()

    report['awards'] = {
        'total': total_awards,
        'by_agency': [{k: r[k] for k in r.keys()} for r in awards_by_agency],
        'completeness': {k: award_completeness[k] for k in award_completeness.keys()},
        'dates': {k: award_dates[k] for k in award_dates.keys()},
        'total_award_dollars': sum([r['sum_amount'] for r in awards_by_agency])
    }

    # 4. Recipients & Organizations
    total_recipients = cur.execute(text("SELECT COUNT(*) FROM recipients")).fetchone()[0]
    total_orgs = cur.execute(text("SELECT COUNT(*) FROM organizations")).fetchone()[0]
    org_types = cur.execute(text("SELECT COALESCE(org_type, 'UNKNOWN') as ot, COUNT(*) FROM organizations GROUP BY ot ORDER BY COUNT(*) DESC")).fetchall()
    recip_types = cur.execute(text("SELECT COALESCE(recipient_type, 'UNKNOWN') as rt, COUNT(*) FROM recipients GROUP BY rt ORDER BY COUNT(*) DESC")).fetchall()

    recip_intel = cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN total_funding_received > 0 THEN 1 ELSE 0 END) as with_funding_received,
            SUM(COALESCE(total_funding_received, 0)) as sum_funding_received,
            SUM(CASE WHEN total_awards_count > 0 THEN 1 ELSE 0 END) as with_awards_count,
            SUM(COALESCE(total_awards_count, 0)) as sum_awards_count,
            SUM(CASE WHEN website_url IS NOT NULL AND TRIM(website_url) != '' THEN 1 ELSE 0 END) as with_website,
            SUM(CASE WHEN primary_technology IS NOT NULL AND TRIM(primary_technology) != '' THEN 1 ELSE 0 END) as with_tech,
            SUM(CASE WHEN headquarters_state IS NOT NULL AND TRIM(headquarters_state) != '' THEN 1 ELSE 0 END) as with_state,
            SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as with_lat_lng,
            SUM(CASE WHEN description IS NOT NULL AND TRIM(description) != '' THEN 1 ELSE 0 END) as with_desc
        FROM recipients
    """).fetchone()

    report['recipients_and_orgs'] = {
        'total_recipients': total_recipients,
        'total_organizations': total_orgs,
        'org_types': [{k: r[k] for k in r.keys()} for r in org_types],
        'recip_types': [{k: r[k] for k in r.keys()} for r in recip_types],
        'recip_intelligence': {k: recip_intel[k] for k in recip_intel.keys()}
    }

    # 5. Taxonomy & Knowledge Graph Linkages
    total_categories = cur.execute(text("SELECT COUNT(*) FROM opportunity_categories")).fetchone()[0]
    cat_breakdown = cur.execute(text("SELECT category_type, COUNT(*), COUNT(DISTINCT category_value) FROM opportunity_categories GROUP BY category_type ORDER BY COUNT(*) DESC")).fetchall()
    
    total_restrictions = cur.execute(text("SELECT COUNT(*) FROM opportunity_restrictions")).fetchone()[0]
    rest_breakdown = cur.execute(text("SELECT category, COUNT(*), COUNT(DISTINCT opportunity_id) FROM opportunity_restrictions GROUP BY category ORDER BY COUNT(*) DESC")).fetchall()

    total_relationships = cur.execute(text("SELECT COUNT(*) FROM opportunity_relationships")).fetchone()[0]
    rel_breakdown = cur.execute(text("SELECT relationship_type, COUNT(*), AVG(confidence) FROM opportunity_relationships GROUP BY relationship_type ORDER BY COUNT(*) DESC")).fetchall()

    report['knowledge_graph'] = {
        'total_categories': total_categories,
        'category_types': [{k: r[k] for k in r.keys()} for r in cat_breakdown],
        'total_restrictions': total_restrictions,
        'restriction_categories': [{k: r[k] for k in r.keys()} for r in rest_breakdown],
        'total_relationships': total_relationships,
        'relationship_types': [{k: r[k] for k in r.keys()} for r in rel_breakdown]
    }

    # 6. Additional Intelligence Assets
    report['additional_assets'] = {
        'result_benchmarks': cur.execute(text("SELECT COUNT(*) FROM result_benchmarks")).fetchone()[0],
        'historical_projects': cur.execute(text("SELECT COUNT(*) FROM historical_projects")).fetchone()[0],
        'historical_opportunities': cur.execute(text("SELECT COUNT(*) FROM historical_opportunities")).fetchone()[0],
        'recipient_patents': cur.execute(text("SELECT COUNT(*) FROM recipient_patents")).fetchone()[0],
        'recipient_investments': cur.execute(text("SELECT COUNT(*) FROM recipient_investments")).fetchone()[0],
        'programs': cur.execute(text("SELECT COUNT(*) FROM programs")).fetchone()[0],
        'sources': cur.execute(text("SELECT COUNT(*) FROM sources")).fetchone()[0],
        'proposals': cur.execute(text("SELECT COUNT(*) FROM proposals")).fetchone()[0],
        'project_analyses': cur.execute(text("SELECT COUNT(*) FROM project_analyses")).fetchone()[0],
        'success_stories': cur.execute(text("SELECT COUNT(*) FROM success_stories")).fetchone()[0],
        'contacts': cur.execute(text("SELECT COUNT(*) FROM contacts")).fetchone()[0],
        'opportunity_documents': cur.execute(text("SELECT COUNT(*) FROM opportunity_documents")).fetchone()[0],
        'change_events': cur.execute(text("SELECT COUNT(*) FROM change_events")).fetchone()[0]
    }

    conn.close()

    with open('backend/audit_results_full.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("Successfully generated backend/audit_results_full.json!")

if __name__ == '__main__':
    run_full_database_audit()
