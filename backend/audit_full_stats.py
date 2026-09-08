import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Setup path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.database import engine
from sqlalchemy import text, inspect

def run_audit():
    print(f"Connecting to database engine: {engine.url}")
    report = {
        "timestamp": datetime.now().isoformat(),
        "database_engine": engine.dialect.name,
        "database_url_masked": str(engine.url).split('@')[-1] if '@' in str(engine.url) else str(engine.url),
    }

    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = sorted(inspector.get_table_names())
        report["total_tables"] = len(tables)
        
        table_counts = {}
        table_columns = {}
        for t in tables:
            try:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                table_counts[t] = cnt
                cols = [col["name"] for col in inspector.get_columns(t)]
                table_columns[t] = cols
            except Exception as e:
                table_counts[t] = f"Error: {e}"
        report["table_counts"] = table_counts
        report["table_columns"] = table_columns

        # Detailed opportunities audit
        if "opportunities" in tables:
            opp_stats = {}
            opp_stats["total"] = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
            
            # by agency
            ag_rows = conn.execute(text("""
                SELECT COALESCE(agency, 'None') as ag, COUNT(*) as cnt,
                       SUM(CASE WHEN total_funding > 0 THEN 1 ELSE 0 END) as has_funding,
                       SUM(COALESCE(total_funding, 0)) as total_funding_sum,
                       AVG(CASE WHEN total_funding > 0 THEN total_funding ELSE NULL END) as avg_funding
                FROM opportunities
                GROUP BY agency ORDER BY cnt DESC
            """)).mappings().all()
            opp_stats["by_agency"] = [dict(r) for r in ag_rows]
            
            # by status
            st_rows = conn.execute(text("SELECT COALESCE(status, 'None') as status, COUNT(*) as cnt FROM opportunities GROUP BY status ORDER BY cnt DESC")).mappings().all()
            opp_stats["by_status"] = [dict(r) for r in st_rows]

            # dates
            date_row = conn.execute(text("SELECT MIN(open_date) as min_open, MAX(open_date) as max_open, MIN(close_date) as min_close, MAX(close_date) as max_close, MIN(year) as min_year, MAX(year) as max_year FROM opportunities")).mappings().first()
            opp_stats["date_range"] = dict(date_row) if date_row else {}

            # completeness
            comp_row = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN name IS NOT NULL AND LENGTH(TRIM(name)) > 0 THEN 1 ELSE 0 END) as with_name,
                    SUM(CASE WHEN short_description IS NOT NULL AND LENGTH(TRIM(short_description)) > 20 THEN 1 ELSE 0 END) as with_substantial_desc,
                    SUM(CASE WHEN total_funding > 0 THEN 1 ELSE 0 END) as with_funding,
                    SUM(CASE WHEN close_date IS NOT NULL THEN 1 ELSE 0 END) as with_close_date,
                    SUM(CASE WHEN detail_page_url IS NOT NULL OR source_url IS NOT NULL THEN 1 ELSE 0 END) as with_url,
                    SUM(CASE WHEN solicitation_number IS NOT NULL AND LENGTH(TRIM(solicitation_number)) > 0 THEN 1 ELSE 0 END) as with_solicitation_number,
                    SUM(CASE WHEN target_trl_min IS NOT NULL OR target_trl_max IS NOT NULL THEN 1 ELSE 0 END) as with_trl
                FROM opportunities
            """)).mappings().first()
            opp_stats["completeness"] = dict(comp_row) if comp_row else {}

            # sample open opportunities
            sample_opps = conn.execute(text("SELECT id, solicitation_number, name, agency, status, open_date, close_date, total_funding FROM opportunities WHERE status ILIKE 'open%' OR status = 'active' ORDER BY close_date DESC NULLS LAST LIMIT 10")).mappings().all()
            opp_stats["sample_open"] = [dict(r) for r in sample_opps]

            report["opportunities_audit"] = opp_stats

        # Detailed awards audit
        if "awards" in tables:
            award_stats = {}
            award_stats["total"] = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar()
            
            # by agency
            ag_rows = conn.execute(text("""
                SELECT COALESCE(agency, 'None') as ag, COUNT(*) as cnt,
                       SUM(CASE WHEN award_amount > 0 THEN 1 ELSE 0 END) as has_amount,
                       SUM(COALESCE(award_amount, 0)) as total_amount_sum,
                       AVG(CASE WHEN award_amount > 0 THEN award_amount ELSE NULL END) as avg_amount
                FROM awards
                GROUP BY agency ORDER BY cnt DESC
            """)).mappings().all()
            award_stats["by_agency"] = [dict(r) for r in ag_rows]

            # by year
            yr_rows = conn.execute(text("SELECT year, COUNT(*) as cnt, SUM(COALESCE(award_amount, 0)) as sum_amount FROM awards WHERE year IS NOT NULL GROUP BY year ORDER BY year DESC LIMIT 15")).mappings().all()
            award_stats["by_recent_years"] = [dict(r) for r in yr_rows]

            # total dollars
            tot_dollars = conn.execute(text("SELECT SUM(award_amount) FROM awards")).scalar()
            award_stats["total_dollars_tracked"] = float(tot_dollars) if tot_dollars else 0.0

            # completeness
            comp_row = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN recipient_name IS NOT NULL AND LENGTH(TRIM(recipient_name)) > 0 THEN 1 ELSE 0 END) as with_recipient,
                    SUM(CASE WHEN award_amount > 0 THEN 1 ELSE 0 END) as with_amount,
                    SUM(CASE WHEN project_title IS NOT NULL AND LENGTH(TRIM(project_title)) > 0 THEN 1 ELSE 0 END) as with_title,
                    SUM(CASE WHEN project_abstract IS NOT NULL AND LENGTH(TRIM(project_abstract)) > 20 THEN 1 ELSE 0 END) as with_abstract,
                    SUM(CASE WHEN recipient_state IS NOT NULL AND LENGTH(TRIM(recipient_state)) > 0 THEN 1 ELSE 0 END) as with_state,
                    SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as with_lat_lng,
                    SUM(CASE WHEN opportunity_id IS NOT NULL THEN 1 ELSE 0 END) as with_opp_fk
                FROM awards
            """)).mappings().first()
            award_stats["completeness"] = dict(comp_row) if comp_row else {}

            report["awards_audit"] = award_stats

        # Detailed Recipients audit
        if "recipients" in tables:
            recip_stats = {}
            recip_stats["total"] = conn.execute(text("SELECT COUNT(*) FROM recipients")).scalar()
            
            comp_row = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN total_funding_received > 0 THEN 1 ELSE 0 END) as with_funding,
                    SUM(COALESCE(total_funding_received, 0)) as sum_funding,
                    SUM(CASE WHEN website_url IS NOT NULL AND LENGTH(TRIM(website_url)) > 0 THEN 1 ELSE 0 END) as with_website,
                    SUM(CASE WHEN primary_technology IS NOT NULL AND LENGTH(TRIM(primary_technology)) > 0 THEN 1 ELSE 0 END) as with_tech,
                    SUM(CASE WHEN headquarters_state IS NOT NULL AND LENGTH(TRIM(headquarters_state)) > 0 THEN 1 ELSE 0 END) as with_state,
                    SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as with_lat_lng,
                    SUM(CASE WHEN description IS NOT NULL AND LENGTH(TRIM(description)) > 0 THEN 1 ELSE 0 END) as with_desc
                FROM recipients
            """)).mappings().first()
            recip_stats["metrics"] = dict(comp_row) if comp_row else {}
            
            top_recipients = conn.execute(text("SELECT name, headquarters_state, total_funding_received, total_awards_count, primary_technology FROM recipients ORDER BY total_funding_received DESC NULLS LAST LIMIT 10")).mappings().all()
            recip_stats["top_10"] = [dict(r) for r in top_recipients]
            report["recipients_audit"] = recip_stats

        # VC & Patents audit
        if "recipient_investments" in tables:
            vc_cols = table_columns.get("recipient_investments", [])
            vc_stats = {}
            vc_stats["total_rounds"] = conn.execute(text("SELECT COUNT(*) FROM recipient_investments")).scalar()
            vc_stats["total_recipients_with_vc"] = conn.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_investments")).scalar()
            amt_col = "amount_usd" if "amount_usd" in vc_cols else ("funding_amount" if "funding_amount" in vc_cols else ("amount" if "amount" in vc_cols else None))
            if amt_col:
                vc_stats["total_vc_amount"] = conn.execute(text(f"SELECT SUM({amt_col}) FROM recipient_investments")).scalar()
            sample_vc = conn.execute(text("SELECT * FROM recipient_investments LIMIT 5")).mappings().all()
            vc_stats["sample_deals"] = [dict(r) for r in sample_vc]
            report["vc_audit"] = vc_stats

        if "recipient_patents" in tables:
            pat_stats = {}
            pat_stats["total_patents"] = conn.execute(text("SELECT COUNT(*) FROM recipient_patents")).scalar()
            pat_stats["recipients_with_patents"] = conn.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_patents")).scalar()
            sample_pat = conn.execute(text("SELECT * FROM recipient_patents LIMIT 5")).mappings().all()
            pat_stats["sample_patents"] = [dict(r) for r in sample_pat]
            report["patents_audit"] = pat_stats

        # Additional intelligence layers
        layer_tables = [
            "interconnection_queue_projects", "national_lab_facilities", "sec_form_d_filings",
            "federal_scaleup_allocations", "federal_procurement_contracts", "der_market_deployments",
            "university_licensable_technologies", "policy_standards", "regulatory_proceedings",
            "opportunity_relationships", "opportunity_categories", "opportunity_restrictions",
            "contacts", "reports", "result_artifacts", "news_items", "proposals", "organizations",
            "technologies", "sources", "programs", "users"
        ]
        layer_stats = {}
        for lt in layer_tables:
            if lt in tables:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{lt}"')).scalar()
                sample = conn.execute(text(f'SELECT * FROM "{lt}" LIMIT 2')).mappings().all()
                layer_stats[lt] = {
                    "count": cnt,
                    "sample": [dict(s) for s in sample]
                }
        report["intelligence_layers"] = layer_stats

    # Write output to json
    out_path = backend_dir / "audit_valuation_dump.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Audit completed successfully! Saved to {out_path}")
    print(f"Total tables: {report['total_tables']}")
    print(f"Opportunities count: {report.get('opportunities_audit', {}).get('total')}")
    print(f"Awards count: {report.get('awards_audit', {}).get('total')}")
    print(f"Total award dollars tracked: ${report.get('awards_audit', {}).get('total_dollars_tracked', 0):,.2f}")

if __name__ == "__main__":
    run_audit()
