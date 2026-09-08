import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("=== DATA PROVENANCE AND SOURCES AUDIT ===")
    sources = conn.execute(text("SELECT * FROM sources ORDER BY id LIMIT 15")).mappings().all()
    for s in sources:
        print(f"  - [{s.get('source_type')}] {s.get('name')}: {s.get('record_count')} records | URL: {s.get('url') or s.get('base_url')}")

    print("\n=== FIELD PROVENANCES ===")
    fp_cnt = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT source_organization), COUNT(DISTINCT entity_type) FROM field_provenances")).fetchall()
    print(f"Total field provenances: {fp_cnt[0][0]}, Source orgs: {fp_cnt[0][1]}, Entity types: {fp_cnt[0][2]}")

    print("\n=== SAMPLE AWARDS PROVENANCE ===")
    award_samples = conn.execute(text("SELECT agency, source_name, external_award_id, recipient_name, award_amount, year FROM awards ORDER BY id DESC LIMIT 5")).mappings().all()
    for a in award_samples:
        print(f"  - [{a['agency']}] {a['source_name']} | Ext ID: {a['external_award_id']} | {a['recipient_name']} | ${a['award_amount'] or 0:,.2f} | Year: {a['year']}")

    print("\n=== SAMPLE OPPORTUNITIES PROVENANCE ===")
    opp_samples = conn.execute(text("SELECT agency, source_name, solicitation_number, name, status, total_funding FROM opportunities ORDER BY id DESC LIMIT 5")).mappings().all()
    for o in opp_samples:
        print(f"  - [{o['agency']}] {o['source_name']} | Sol #: {o['solicitation_number']} | {o['name'][:50]} | Status: {o['status']} | Funding: ${o['total_funding'] or 0:,.2f}")

    print("\n=== CONTACTS AUDIT ===")
    contact_stats = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT email), COUNT(DISTINCT organization_id) FROM contacts")).fetchall()
    print(f"Contacts: {contact_stats[0][0]} total, {contact_stats[0][1]} unique emails, {contact_stats[0][2]} orgs")
    sample_contacts = conn.execute(text("SELECT full_name, title, email, phone, organization_name, department FROM contacts LIMIT 5")).mappings().all()
    for c in sample_contacts:
        print(f"  - {c['full_name']} ({c['title']}) at {c['organization_name']} | {c['email']}")

    print("\n=== RECIPIENT INTEL AUDIT ===")
    recip_stats = conn.execute(text("SELECT COUNT(*), COUNT(DISTINCT name), SUM(CASE WHEN total_funding_received > 0 THEN 1 ELSE 0 END) FROM recipients")).fetchall()
    print(f"Recipients: {recip_stats[0][0]} total, {recip_stats[0][1]} unique names, {recip_stats[0][2]} with funding")

