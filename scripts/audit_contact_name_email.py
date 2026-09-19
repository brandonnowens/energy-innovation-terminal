import csv, os, sys, re
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

PERSONAL_DOMAINS = {'gmail.com','yahoo.com','hotmail.com','outlook.com','icloud.com','protonmail.com','aol.com','live.com','msn.com','me.com'}

def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip()).lower()

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute('''
    SELECT id, name_first, name_last, name_display,
           email, email_status, email_deliverable,
           awards_count, role_type, institution_name
    FROM contacts ORDER BY awards_count DESC NULLS LAST
''')

issues = []
for row in cur.fetchall():
    cid, first, last, display, email, email_status, email_deliverable, awards, role_type, institution_name = row
    flags = []
    full = norm(f'{first or } {last or }').strip()
    disp = norm(display or '')
    if full and disp and full != disp:
        flags.append(f'name_mismatch: display={repr(display)} vs first+last={repr(first)} {repr(last)}')
    if email and awards and awards > 0:
        domain = email.split('@')[-1].lower() if '@' in email else ''
        if domain in PERSONAL_DOMAINS:
            flags.append(f'personal_email_high_award: domain={domain} awards={awards}')
    if email_status == 'gateway_required' and institution_name:
        flags.append(f'gateway_required_institutional: institution={repr(institution_name)}')
    if flags:
        issues.append({'contact_id': cid,'name_display': display,'name_first': first,'name_last': last,'email': email,'email_status': email_status,'awards_count': awards,'role_type': role_type,'institution_name': institution_name,'flags': ' | '.join(flags)})

cur.close()

report_dir = script_dir.parent / 'reports'
report_dir.mkdir(exist_ok=True)
out_path = report_dir / 'contact_name_email_mismatch_audit.csv'
fieldnames = ['contact_id','name_display','name_first','name_last','email','email_status','awards_count','role_type','institution_name','flags']
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(issues)
print(f'Found {len(issues)} contacts with issues -> {out_path}')

conn2 = psycopg2.connect(db_url)
cur2 = conn2.cursor()
inserted = 0
for issue in issues:
    if 'name_mismatch' in issue['flags'] and (issue['awards_count'] or 0) > 0:
        cur2.execute('SELECT id FROM data_quality_issues WHERE entity_type=%s AND entity_id=%s AND issue_type=%s LIMIT 1', ('contact', issue['contact_id'], 'name_display_mismatch'))
        if not cur2.fetchone():
            cur2.execute('''INSERT INTO data_quality_issues (entity_type, entity_id, issue_type, severity, description, suggested_fix, resolved) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                ('contact', issue['contact_id'], 'name_display_mismatch', 'medium',
                 f'name_display={repr(issue[" name_display\])} does not match {repr(issue[\name_first\])} {repr(issue[\name_last\])}',
 f'UPDATE contacts SET name_display=trim(concat_ws(chr(32),name_first,name_last)) WHERE id={issue[\contact_id\]}',
 False))
 inserted += 1
conn2.commit()
cur2.close(); conn2.close()
print(f'Inserted {inserted} data_quality_issues rows for name mismatches on award-linked contacts')
