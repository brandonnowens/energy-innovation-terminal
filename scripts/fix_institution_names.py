import os, sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent / 'backend'
env_file = backend_dir / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            os.environ.setdefault(k.strip(), v.strip())

raw_url = os.environ.get('DATABASE_URL', '')
db_url = raw_url.replace('postgresql+psycopg2://', 'postgresql://')
if not db_url:
    print('ERROR: DATABASE_URL not set'); sys.exit(1)

import psycopg2

DOMAIN_TO_INSTITUTION = {
    'coned.com': 'Consolidated Edison','conedison.com': 'Consolidated Edison',
    'nationalgrid.com': 'National Grid','eversource.com': 'Eversource Energy',
    'pge.com': 'Pacific Gas & Electric','sce.com': 'Southern California Edison',
    'sdge.com': 'San Diego Gas & Electric','duke-energy.com': 'Duke Energy',
    'dominion.com': 'Dominion Energy','dominionenergy.com': 'Dominion Energy',
    'exeloncorp.com': 'Exelon Corporation','peco.com': 'PECO Energy',
    'bge.com': 'Baltimore Gas and Electric','comed.com': 'ComEd',
    'pse.com': 'Puget Sound Energy','xcelenergy.com': 'Xcel Energy',
    'pseg.com': 'PSEG','tva.gov': 'Tennessee Valley Authority',
    'nypa.gov': 'New York Power Authority','lipa.com': 'Long Island Power Authority',
    'lipower.org': 'Long Island Power Authority','caiso.com': 'CAISO',
    'pjm.com': 'PJM Interconnection','iso-ne.com': 'ISO New England',
    'miso.energy': 'MISO','ercot.com': 'ERCOT','swpp.org': 'Southwest Power Pool',
}
WRONG_PATTERNS = ['nyserda', 'new york state energy research', 'nrdc', 'rmi', 'environmental defense']

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute('''
    SELECT id, name_display, email, role_type, institution_name, email_domain, email_status, awards_count
    FROM contacts WHERE role_type IN (''utility_lead'', ''institutional_gateway'') ORDER BY role_type, id
''')
rows = cur.fetchall()
print(f'Found {len(rows)} utility_lead / institutional_gateway contacts')

corrections = []
ambiguous = []
for row in rows:
    cid, name_display, email, role_type, institution_name, email_domain, email_status, awards_count = row
    domain = (email_domain or '').lower()
    inst = (institution_name or '').lower()
    if domain in DOMAIN_TO_INSTITUTION:
        correct_inst = DOMAIN_TO_INSTITUTION[domain]
        if institution_name != correct_inst:
            corrections.append({'id': cid,'name': name_display,'old_institution': institution_name,'new_institution': correct_inst,'reason': f'email domain {domain}'})
        continue
    if role_type == 'utility_lead':
        for pattern in WRONG_PATTERNS:
            if pattern in inst:
                ambiguous.append({'id': cid,'name': name_display,'email': email,'role_type': role_type,'institution_name': institution_name,'flag': f'utility_lead labeled as NGO/agency: {repr(institution_name)}'})
                break

print(f'Domain-based corrections: {len(corrections)}, Ambiguous: {len(ambiguous)}')
fixed = 0
for c in corrections:
    print(f'  FIX id={c[" id\]}: {repr(c[\old_institution\])} -> {repr(c[\new_institution\])} ({c[\reason\]})')
 cur.execute('UPDATE contacts SET institution_name=%s, updated_at=NOW() WHERE id=%s', (c['new_institution'], c['id']))
 fixed += 1
conn.commit()
print(f'Applied {fixed} corrections')

reviewed = 0
for a in ambiguous:
 cur.execute('SELECT id FROM entity_merge_reviews WHERE entity_type=%s AND entity_id_a=%s AND review_reason LIKE %s LIMIT 1', ('contact', a['id'], 'utility_lead_institution%%'))
 if not cur.fetchone():
 cur.execute('INSERT INTO entity_merge_reviews (entity_type, entity_id_a, entity_id_b, review_reason, status, notes) VALUES (%s,%s,%s,%s,%s,%s)',
 ('contact', a['id'], None, 'utility_lead_institution_mismatch', 'pending', a['flag']))
 reviewed += 1
conn.commit()
cur.close(); conn.close()
print(f'Inserted {reviewed} entity_merge_reviews for manual review')
print('Done.')
