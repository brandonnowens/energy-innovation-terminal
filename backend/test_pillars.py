import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.engine.win_rate_engine import calculate_win_rate_analytics
from app.engine.teaming_engine import generate_teaming_stack
from app.ingest.health_monitor import get_pipeline_health_summary, run_quick_url_health_audit
from app.models.opportunity import Opportunity

db = SessionLocal()
opp = db.query(Opportunity).filter(Opportunity.status == 'open').first()
if not opp:
    opp = db.query(Opportunity).first()

print("=== 1. TESTING WIN RATE ENGINE ===")
wr = calculate_win_rate_analytics(db, opp, fit_score=0.82)
print("Opp:", opp.solicitation_number or opp.id, "| Agency:", opp.agency)
print(f"Win Probability: {wr['win_probability_pct']}% | Tier: {wr['win_tier']}")
print(f"Precedent Rating: {wr['precedent_rating']}")
print(f"Field Size: {wr['estimated_field_size']}")
print(f"Advantages: {wr['key_advantages']}")

print("\n=== 2. TESTING TEAMING ENGINE ===")
team = generate_teaming_stack(db, opp_id=opp.id)
print(f"Consortia Composition: {team['consortia_composition']}")
for p in team['recommended_partners']:
    print(f"  * {p['role_title']}: {p['name']} (PI: {p['pi_name']} <{p['pi_email']}>) - {p['location']}")

print("\n=== 3. TESTING FEED HEALTH MONITOR ===")
health = get_pipeline_health_summary(db)
print(f"Overall Health: {health['overall_health']}")
print(f"Total Feeds Tracked: {len(health['feed_telemetry'])}")
audit = run_quick_url_health_audit(db, sample_size=5)
print(f"Liveness sample pct: {audit['liveness_pct']}%")

print("\nALL 3 CAPABILITIES TESTED SUCCESSFULLY!")
db.close()
