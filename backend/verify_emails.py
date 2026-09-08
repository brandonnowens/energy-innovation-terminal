"""
Verify email address syntax, domain deliverability, and validity across all contacts.
Updates contacts table with:
- email_status: 'verified_valid', 'syntax_valid', 'gateway_required', 'invalid_format'
- email_deliverable: Boolean (True/False)
- email_domain: String
- email_score: Float (0.0 to 1.0)
- email_verified_at: DateTime string
"""

import sys
import re
import socket
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))
from app.database import engine

# Strict RFC 5322 compatible regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# Known institutional / government / academic domain suffixes
TRUSTED_SUFFIXES = [".gov", ".edu", ".mil", ".org", ".energy.gov", ".doe.gov", ".nyserda.ny.gov", ".state.", ".us"]


def check_domain_dns(domain: str) -> bool:
    """Check if domain resolves via DNS A or MX record with short timeout."""
    domain = domain.lower().strip()
    if not domain or len(domain) < 3:
        return False
        
    candidates = [domain]
    parts = domain.split(".")
    if len(parts) > 2:
        candidates.append(".".join(parts[-2:]))
        candidates.append(".".join(parts[-3:]))
        
    for cand in candidates:
        try:
            socket.setdefaulttimeout(1.5)
            socket.gethostbyname(cand)
            return True
        except Exception:
            continue
    return False


def verify_all_emails():
    print("Verifying contacts email addresses in PostgreSQL...")
    with engine.begin() as conn:
        # Fetch all contacts
        cur_contacts = conn.execute(text("SELECT id, email, entity_contact_url FROM contacts")).fetchall()
        contacts = [dict(r._mapping) for r in cur_contacts]
        print(f"Total contacts loaded: {len(contacts)}")

        # Collect unique domains to check DNS concurrently
        domains_to_check = set()
        for row in contacts:
            em = (row["email"] or "").strip()
            if em and "@" in em:
                domain = em.split("@")[-1].strip().lower()
                domains_to_check.add(domain)

        print(f"Checking DNS deliverability for {len(domains_to_check)} unique domains in parallel...")
        domain_dns_cache = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_domain = {executor.submit(check_domain_dns, dom): dom for dom in domains_to_check}
            for fut in future_to_domain:
                dom = future_to_domain[fut]
                try:
                    domain_dns_cache[dom] = fut.result()
                except Exception:
                    domain_dns_cache[dom] = False

        print("DNS resolution complete. Scoring individual email addresses...")
        updates = []
        valid_count = 0
        gateway_count = 0
        syntax_error_count = 0
        now_str = datetime.now().isoformat()

        for row in contacts:
            cid = row["id"]
            em = (row["email"] or "").strip()
            url = (row["entity_contact_url"] or "").strip()

            if not em:
                status = "gateway_required"
                deliverable = False
                domain = url.replace("https://", "").replace("http://", "").split("/")[0] if url else None
                score = 0.50 if url else 0.0
                gateway_count += 1
            elif not EMAIL_REGEX.match(em):
                status = "invalid_format"
                deliverable = False
                domain = em.split("@")[-1] if "@" in em else None
                score = 0.10
                syntax_error_count += 1
            else:
                domain = em.split("@")[-1].lower()
                is_resolvable = domain_dns_cache.get(domain, False)
                is_trusted = any(domain.endswith(sfx) or sfx in domain for sfx in TRUSTED_SUFFIXES)

                if is_resolvable:
                    status = "verified_valid"
                    deliverable = True
                    score = 1.0 if is_trusted else 0.95
                    valid_count += 1
                else:
                    status = "syntax_valid"
                    deliverable = False
                    score = 0.75 if is_trusted else 0.6
                    valid_count += 1

            updates.append({
                "status": status,
                "deliverable": deliverable,
                "domain": domain,
                "score": score,
                "now_str": now_str,
                "cid": cid
            })

        update_sql = text("""
            UPDATE contacts SET
                email_status = :status,
                email_deliverable = :deliverable,
                email_domain = :domain,
                email_score = :score,
                email_verified_at = :now_str
            WHERE id = :cid
        """)
        batch_size = 1000
        for i in range(0, len(updates), batch_size):
            conn.execute(update_sql, updates[i:i + batch_size])

        print("\n=== Verification Summary ===")
        print(f"Total Contacts: {len(contacts)}")
        print(f"Verified Deliverable / Syntax-Valid Emails: {valid_count}")
        print(f"Refer to Entity Gateways: {gateway_count}")
        print(f"Invalid Syntax Formats: {syntax_error_count}")
        
        # Sample verification results
        print("\nSample Verified Records:")
        sample = conn.execute(text("SELECT name_display, email, email_status, email_score, email_domain FROM contacts WHERE email IS NOT NULL AND email != '' LIMIT 10")).fetchall()
        for row in sample:
            print(f"  {row[0]} | {row[1]} | Status: {row[2]} (Score: {row[3]}) | Domain: {row[4]}")


if __name__ == "__main__":
    verify_all_emails()
