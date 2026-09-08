import json
from sqlalchemy import text
from app.database import engine


def main():
    print("Phase 3: Financial Backfill")
    with engine.begin() as conn:
        # Process opportunities
        cur_opps = conn.execute(text("SELECT id, raw_source_data, total_funding, award_min, cost_share_pct, expected_awards, total_awarded, award_count_actual FROM opportunities"))
        opportunities = [dict(r._mapping) for r in cur_opps.fetchall()]

        # Awards aggregates by opportunity_id
        cur_awards = conn.execute(text("SELECT opportunity_id, SUM(award_amount) as sum_awards, COUNT(*) as count_awards FROM awards WHERE opportunity_id IS NOT NULL GROUP BY opportunity_id"))
        awards_agg = {r[0]: (r[1] or 0.0, r[2] or 0) for r in cur_awards.fetchall()}

        updated_count = 0
        total = len(opportunities)

        for opp in opportunities:
            opp_id = opp['id']
            updates = {}
            
            # 2. Parse raw_source_data
            if opp['raw_source_data']:
                try:
                    raw_data = json.loads(opp['raw_source_data'])
                    if opp['total_funding'] is None and 'total_funding' in raw_data:
                        updates['total_funding'] = raw_data['total_funding']
                    if opp['award_min'] is None and 'award_min' in raw_data:
                        updates['award_min'] = raw_data['award_min']
                    if opp['cost_share_pct'] is None and 'cost_share_pct' in raw_data:
                        updates['cost_share_pct'] = raw_data['cost_share_pct']
                    if opp['expected_awards'] is None and 'expected_awards' in raw_data:
                        updates['expected_awards'] = raw_data['expected_awards']
                except Exception:
                    pass

            # 3. Cross-reference awards
            if opp_id in awards_agg:
                sum_awards, count_awards = awards_agg[opp_id]
                updates['total_awarded'] = sum_awards
                updates['award_count_actual'] = count_awards
                updates['funding_provenance'] = 'awards_crossref'
            elif updates:
                updates['funding_provenance'] = 'raw_source_data'

            if updates:
                set_clauses = [f"{k} = :{k}" for k in updates]
                updates['opp_id'] = opp_id
                query = text(f"UPDATE opportunities SET {', '.join(set_clauses)} WHERE id = :opp_id")
                conn.execute(query, updates)
                updated_count += 1

        print(f"Opportunities updated with financials: {updated_count} / {total}")


if __name__ == '__main__':
    main()

