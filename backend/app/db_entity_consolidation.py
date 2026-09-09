"""High-Performance Set-Based Entity Deduplication & Organization Consolidation Engine.

Performs conservative, evidence-based deduplication across the recipients, awards,
contacts, and IP attribution tables with full pre-merge backups and atomic transactions.
"""

import os
import sys
import re
import json
import logging
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.recipient import Recipient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EntityConsolidation")


def clean_legal_name(name: str) -> str:
    """Strict corporate entity suffix cleaner preserving campus, domain, and distinct words."""
    if not name:
        return ""
    s = name.strip().lower()
    s = re.sub(r'[\'"`]', '', s)
    s = re.sub(r'[,\.\-\/\(\)\&\+]+', ' ', s)
    tokens = s.split()
    
    legal_suffixes = {
        'inc', 'incorporated', 'llc', 'llp', 'corp', 'corporation',
        'co', 'company', 'ltd', 'limited', 'pllc', 'pbc', 'lp', 'llc.',
        'holdings', 'group'
    }
    
    clean_tokens = [t for t in tokens if t not in legal_suffixes]
    return ' '.join(clean_tokens) if clean_tokens else ' '.join(tokens)


def normalize_alphanumeric(name: str) -> str:
    """Normalize string to lowercase alphanumeric only for exact character equality."""
    if not name:
        return ""
    return re.sub(r'[^a-z0-9]', '', name.lower())


def is_academic_or_gov(name: str) -> bool:
    """Detect universities, national labs, and government agencies which require strict campus preservation."""
    n = name.lower()
    patterns = [
        'university', 'college', 'institute of technology', 'school of',
        'regents of', 'trustees of', 'national laboratory', 'department of',
        'authority', 'commission', 'county', 'city of', 'board of', 'state of'
    ]
    return any(p in n for p in patterns)


def select_best_canonical_master(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Selects the cleanest Title-Cased corporate name with the most complete profile."""
    def score_recipient(r: Dict[str, Any]) -> Tuple[int, int, float, int]:
        name = r.get("name") or ""
        is_all_caps = name.isupper()
        casing_score = 1 if is_all_caps else 3
        has_proper_punctuation = 1 if ("," in name or "." in name) else 0
        richness = 0
        if r.get("description"): richness += 2
        if r.get("website_url"): richness += 2
        if r.get("primary_technology"): richness += 1
        if r.get("headquarters_city"): richness += 1
        funding = float(r.get("total_funding_received") or 0.0)
        awards = int(r.get("total_awards_count") or 0)
        return (casing_score + has_proper_punctuation, richness, funding, awards)

    sorted_cluster = sorted(cluster, key=score_recipient, reverse=True)
    return sorted_cluster[0]


def run_consolidation(dry_run: bool = False) -> Dict[str, Any]:
    """Execute conservative, high-confidence entity deduplication via high-speed set operations."""
    logger.info(f"Starting High-Performance Entity Consolidation (dry_run={dry_run})...")
    
    backup_dir = Path(__file__).parent.parent / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f"recipients_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    
    with SessionLocal() as db:
        # Load all recipient records as clean dictionaries to avoid ORM identity map overhead
        raw_rows = db.execute(text("""
            SELECT id, name, normalized_name, recipient_type, description, primary_technology, sector,
                   headquarters_city, headquarters_state, headquarters_country, is_ny_based,
                   website_url, total_funding_received, total_awards_count, total_nyserda_funding,
                   nyserda_award_count, total_federal_funding, federal_award_count, funded_agencies
            FROM recipients;
        """)).mappings().all()
        
        all_recipients = [dict(r) for r in raw_rows]
        total_initial_recipients = len(all_recipients)
        logger.info(f"Total recipients loaded from database: {total_initial_recipients}")
        
        # Step 1: Save full snapshot
        if not dry_run:
            with open(backup_file, "w", encoding="utf-8") as bf:
                json.dump(all_recipients, bf, indent=2)
            logger.info(f"Saved full database backup of {len(all_recipients)} recipients to {backup_file}")
            
        # Step 2: Form candidate clusters
        groups = defaultdict(list)
        for r in all_recipients:
            key = clean_legal_name(r["name"])
            if key:
                groups[key].append(r)
                
        high_confidence_clusters: List[Tuple[str, List[Dict[str, Any]], str]] = []
        preserved_clusters: List[Tuple[str, List[Dict[str, Any]], str]] = []
        
        for key, cluster in groups.items():
            if len(cluster) <= 1:
                continue
                
            is_academic = any(is_academic_or_gov(r["name"]) for r in cluster)
            states = set(r["headquarters_state"].strip().upper() for r in cluster if r.get("headquarters_state") and str(r["headquarters_state"]).strip())
            cities = set(r["headquarters_city"].strip().title() for r in cluster if r.get("headquarters_city") and str(r["headquarters_city"]).strip())
            is_short = len(key) <= 4 or (len(key.split()) == 1 and len(key) <= 5)
            
            # Case 1: Academic / Government Entity
            if is_academic:
                raw_norms = set(normalize_alphanumeric(r["name"]) for r in cluster)
                if len(raw_norms) == 1:
                    high_confidence_clusters.append((key, cluster, "Academic entity with 100% identical alphanumeric name"))
                else:
                    preserved_clusters.append((key, cluster, "Academic entity with distinct campuses/entities - preserved"))
                continue
                
            # Case 2: Short / Acronym name
            if is_short:
                raw_norms = set(normalize_alphanumeric(r["name"]) for r in cluster)
                if len(raw_norms) == 1 and len(states) <= 1:
                    high_confidence_clusters.append((key, cluster, "Short acronym entity with exact alphanumeric and state match"))
                else:
                    preserved_clusters.append((key, cluster, "Short acronym with multiple potential distinct meanings - preserved"))
                continue
                
            # Case 3: Commercial Companies / Clean Tech Innovators
            if len(states) <= 1 or (len(states) == 2 and 'DC' in states) or (len(cities) <= 1 and len(cities) > 0):
                high_confidence_clusters.append((key, cluster, "Corporate entity with matching/compatible geography and legal name"))
            else:
                preserved_clusters.append((key, cluster, f"Corporate entity across distinct states {states} - preserved"))
                
        logger.info(f"Analyzed clusters: {len(high_confidence_clusters)} High-Confidence to merge, {len(preserved_clusters)} Preserved distinct.")
        
        # Step 3: Execute Consolidation via set-based SQL statements
        all_subordinate_ids: List[int] = []
        all_name_replacements: Dict[str, str] = {} # subordinate_name -> canonical_name
        
        consolidated_count = 0
        
        for key, cluster, reason in high_confidence_clusters:
            master = select_best_canonical_master(cluster)
            subordinates = [r for r in cluster if r["id"] != master["id"]]
            
            sub_ids = [r["id"] for r in subordinates]
            sub_names = [r["name"] for r in subordinates]
            all_subordinate_ids.extend(sub_ids)
            for sn in sub_names:
                all_name_replacements[sn] = master["name"]
                
            # Aggregate metrics
            total_funding = sum(float(r.get("total_funding_received") or 0.0) for r in cluster)
            total_awards = sum(int(r.get("total_awards_count") or 0) for r in cluster)
            total_nyserda_funding = sum(float(r.get("total_nyserda_funding") or 0.0) for r in cluster)
            nyserda_awards = sum(int(r.get("nyserda_award_count") or 0) for r in cluster)
            total_federal_funding = sum(float(r.get("total_federal_funding") or 0.0) for r in cluster)
            federal_awards = sum(int(r.get("federal_award_count") or 0) for r in cluster)
            
            agency_set = set()
            for r in cluster:
                if r.get("funded_agencies"):
                    for ag in str(r["funded_agencies"]).split(","):
                        if ag.strip():
                            agency_set.add(ag.strip())
                            
            merged_agencies = ", ".join(sorted(agency_set)) if agency_set else master.get("funded_agencies")
            
            # Fill missing enriched fields
            web = master.get("website_url") or next((s.get("website_url") for s in subordinates if s.get("website_url")), None)
            desc = master.get("description") or next((s.get("description") for s in subordinates if s.get("description")), None)
            tech = master.get("primary_technology") or next((s.get("primary_technology") for s in subordinates if s.get("primary_technology")), None)
            sector = master.get("sector") or next((s.get("sector") for s in subordinates if s.get("sector")), None)
            city = master.get("headquarters_city") or next((s.get("headquarters_city") for s in subordinates if s.get("headquarters_city")), None)
            state = master.get("headquarters_state") or next((s.get("headquarters_state") for s in subordinates if s.get("headquarters_state")), None)
            is_ny = bool(master.get("is_ny_based") or any(s.get("is_ny_based") for s in subordinates))
            norm_name = master["name"].lower().strip()
            
            if not dry_run:
                db.execute(text("""
                    UPDATE recipients
                    SET total_funding_received = :f,
                        total_awards_count = :a,
                        total_nyserda_funding = :ny_f,
                        nyserda_award_count = :ny_a,
                        total_federal_funding = :fed_f,
                        federal_award_count = :fed_a,
                        funded_agencies = :ag,
                        website_url = :web,
                        description = :desc,
                        primary_technology = :tech,
                        sector = :sector,
                        headquarters_city = :city,
                        headquarters_state = :state,
                        is_ny_based = :is_ny,
                        normalized_name = :norm,
                        updated_at = NOW()
                    WHERE id = :mid;
                """), {
                    "f": total_funding,
                    "a": total_awards,
                    "ny_f": total_nyserda_funding,
                    "ny_a": nyserda_awards,
                    "fed_f": total_federal_funding,
                    "fed_a": federal_awards,
                    "ag": merged_agencies,
                    "web": web,
                    "desc": desc,
                    "tech": tech,
                    "sector": sector,
                    "city": city,
                    "state": state,
                    "is_ny": is_ny,
                    "norm": norm_name,
                    "mid": master["id"]
                })
                
                # Re-link recipient_patents and recipient_investments for this cluster
                if sub_ids:
                    db.execute(text("UPDATE recipient_patents SET recipient_id = :mid WHERE recipient_id = ANY(:sids);"), {"mid": master["id"], "sids": sub_ids})
                    db.execute(text("UPDATE recipient_investments SET recipient_id = :mid WHERE recipient_id = ANY(:sids);"), {"mid": master["id"], "sids": sub_ids})

            consolidated_count += 1
            
        logger.info(f"Prepared batch updates for {consolidated_count} canonical master recipients.")
        
        total_awards_relinked = 0
        total_patents_relinked = 0
        total_contacts_relinked = 0
        
        if not dry_run and all_name_replacements:
            logger.info("Executing set-based name updates across awards, patents, and contacts...")
            
            # Batch update awards
            for old_name, new_name in all_name_replacements.items():
                res_aw = db.execute(text("UPDATE awards SET recipient_name = :n WHERE recipient_name = :o;"), {"n": new_name, "o": old_name})
                total_awards_relinked += res_aw.rowcount
                res_pat = db.execute(text("UPDATE recipient_patents SET assignee_name = :n WHERE assignee_name = :o;"), {"n": new_name, "o": old_name})
                total_patents_relinked += res_pat.rowcount
                res_con = db.execute(text("UPDATE contacts SET institution_name = :n WHERE institution_name = :o;"), {"n": new_name, "o": old_name})
                total_contacts_relinked += res_con.rowcount
                
            # Delete all subordinate recipient rows in one batch
            if all_subordinate_ids:
                logger.info(f"Purging {len(all_subordinate_ids)} redundant subordinate recipient rows...")
                db.execute(text("DELETE FROM recipients WHERE id = ANY(:sids);"), {"sids": all_subordinate_ids})
                
            db.commit()
            logger.info("Successfully committed all consolidation changes to PostgreSQL!")
        else:
            db.rollback()
            logger.info("Dry run completed without modifications.")
            
        final_count = db.execute(text("SELECT COUNT(*) FROM recipients;")).scalar()
        logger.info(f"Recipients before: {total_initial_recipients} -> Recipients after: {final_count}")
        
        return {
            "initial_recipients": total_initial_recipients,
            "final_recipients": final_count,
            "clusters_merged": consolidated_count,
            "rows_purged": len(all_subordinate_ids),
            "awards_relinked": total_awards_relinked,
            "patents_relinked": total_patents_relinked,
            "contacts_relinked": total_contacts_relinked,
            "backup_file": str(backup_file)
        }


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    res = run_consolidation(dry_run=is_dry)
    print("\nResult:", json.dumps(res, indent=2))
