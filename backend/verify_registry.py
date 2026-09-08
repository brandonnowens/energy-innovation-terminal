import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.ingest.state_utility_registry import get_ordered_states, STATE_GDP_RANKING, STATE_UTILITY_DATA

states = get_ordered_states()
print(f"Total ranked jurisdictions: {len(states)}")
total_utils = sum(len(s.get('utilities', [])) for s in states)
print(f"Total utilities in registry: {total_utils}")

total_opps = 0
total_awards = 0
for s in states:
    u_names = [u['name'] for u in s.get('utilities', [])]
    opp_count = sum(len(u.get('opportunities', [])) for u in s.get('utilities', []))
    awd_count = sum(len(u.get('awards', [])) for u in s.get('utilities', []))
    total_opps += opp_count
    total_awards += awd_count
    print(f"Rank {s['rank']:2d} | {s['state_code']} ({s['state_name']} - ${s['gdp_billions']}B): {len(u_names)} utilities, {opp_count} opps, {awd_count} awards -> {u_names}")

print(f"\nTOTAL NATIONWIDE OPPORTUNITIES DEFINED: {total_opps}")
print(f"TOTAL NATIONWIDE AWARDS DEFINED: {total_awards}")
