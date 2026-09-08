from datetime import datetime
from sqlalchemy import text
from app.database import engine


def main():
    print("Phase 5: Programs Expansion")
    with engine.begin() as conn:
        # 1. Create inferred programs
        inferred_programs = [
            # DOE
            ('DOE EERE', 'inferred'), ('DOE Office of Science', 'inferred'),
            ('DOE OCED', 'inferred'), ('DOE FECM', 'inferred'),
            ('DOE Fossil Energy', 'inferred'), ('DOE General', 'inferred'),
            # NSF
            ('NSF TIP', 'inferred'), ('NSF Engineering', 'inferred'),
            ('NSF CISE', 'inferred'), ('NSF General', 'inferred'),
            # ARPA-E
            ('ARPA-E Programs', 'inferred'),
            # EPA
            ('EPA Research', 'inferred'), ('EPA SBIR', 'inferred'),
            ('EPA General', 'inferred')
        ]
        
        # Get other agencies with > 1 opp
        other_agencies = conn.execute(text("SELECT agency, COUNT(*) as c FROM opportunities WHERE agency NOT IN ('NYSERDA', 'DOE', 'NSF', 'ARPA-E', 'EPA') GROUP BY agency HAVING COUNT(*) > 1")).fetchall()
        for row in other_agencies:
            if row[0]:
                inferred_programs.append((f"{row[0]} General", 'inferred'))

        # Insert if not exists
        existing_programs = {r[0] for r in conn.execute(text("SELECT name FROM programs")).fetchall()}
        
        insert_prog_sql = text("""
            INSERT INTO programs (name, program_type, active, last_verified_at, created_at, updated_at) 
            VALUES (:name, :ptype, true, :now_str, :now_str, :now_str)
        """)
        now_str = datetime.now().isoformat()
        for name, ptype in inferred_programs:
            if name not in existing_programs:
                conn.execute(insert_prog_sql, {"name": name, "ptype": ptype, "now_str": now_str})

        # Refresh existing programs mapping
        programs = conn.execute(text("SELECT id, name FROM programs")).fetchall()
        prog_map = {r[1]: r[0] for r in programs}

        # 2. Link opportunities to programs
        opportunities = conn.execute(text("SELECT id, agency, agency_code, keywords, name FROM opportunities")).fetchall()

        linked_count = 0
        updates = []

        for opp in opportunities:
            opp_id = opp[0]
            agency = opp[1] or ''
            agency_code = opp[2] or ''
            text_blob = (opp[3] or '') + " " + (opp[4] or '')
            text_lower = text_blob.lower()
            
            prog_id = None
            
            if agency == 'NYSERDA':
                # Match to existing 14 programs (heuristic)
                for p_name, p_id in prog_map.items():
                    if p_name.lower() in text_lower:
                        prog_id = p_id
                        break
            elif agency == 'DOE':
                if 'eere' in agency_code.lower() or 'eere' in text_lower: prog_id = prog_map.get('DOE EERE')
                elif 'science' in agency_code.lower() or 'science' in text_lower: prog_id = prog_map.get('DOE Office of Science')
                elif 'oced' in agency_code.lower() or 'oced' in text_lower: prog_id = prog_map.get('DOE OCED')
                elif 'fecm' in agency_code.lower() or 'fecm' in text_lower: prog_id = prog_map.get('DOE FECM')
                elif 'fossil' in text_lower: prog_id = prog_map.get('DOE Fossil Energy')
                else: prog_id = prog_map.get('DOE General')
            elif agency == 'NSF':
                if 'tip' in text_lower: prog_id = prog_map.get('NSF TIP')
                elif 'engineering' in text_lower: prog_id = prog_map.get('NSF Engineering')
                elif 'cise' in text_lower: prog_id = prog_map.get('NSF CISE')
                else: prog_id = prog_map.get('NSF General')
            elif agency == 'ARPA-E':
                prog_id = prog_map.get('ARPA-E Programs')
            elif agency == 'EPA':
                if 'research' in text_lower: prog_id = prog_map.get('EPA Research')
                elif 'sbir' in text_lower: prog_id = prog_map.get('EPA SBIR')
                else: prog_id = prog_map.get('EPA General')
            else:
                prog_id = prog_map.get(f"{agency} General")
                
            if prog_id:
                updates.append({"prog_id": prog_id, "opp_id": opp_id})
                linked_count += 1

        update_opp_sql = text("UPDATE opportunities SET program_id = :prog_id WHERE id = :opp_id")
        batch_size = 1000
        for i in range(0, len(updates), batch_size):
            conn.execute(update_opp_sql, updates[i:i + batch_size])

        print(f"Programs expanded and linked to {linked_count} opportunities.")


if __name__ == '__main__':
    main()

