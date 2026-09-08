import json

with open("backend/audit_valuation_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

opps = data.get("opportunities_audit", {})
print("=== OPPORTUNITIES BY AGENCY ===")
for ag in opps.get("by_agency", []):
    print(f"  {ag['ag']}: {ag['cnt']} opps, ${ag['total_funding_sum']:,.2f}")

print("\n=== OPPORTUNITIES BY STATUS ===")
for st in opps.get("by_status", []):
    print(f"  {st['status']}: {st['cnt']}")

print("\n=== SAMPLE ACTIVE/OPEN OPPS ===")
for op in opps.get("sample_open", []):
    print(f"  [{op['agency']}] {op['solicitation_number']}: {op['name'][:60]}... | Status: {op['status']} | Closes: {op['close_date']} | Funding: ${op['total_funding'] or 0:,.2f}")

print("\n=== TOTAL AWARDS BY AGENCY TOP 15 ===")
awards = data.get("awards_audit", {})
for ag in awards.get("by_agency", [])[:15]:
    print(f"  {ag['ag']}: {ag['cnt']} awards, ${ag['total_amount_sum']:,.2f}")
