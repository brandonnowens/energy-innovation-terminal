"""Schema migration v3: Organizations, Contacts, Community, Strategy, Reports."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

from app.database import engine
from sqlalchemy import text, inspect

def run_migration():
    insp = inspect(engine)
    existing = set(insp.get_table_names())

    with engine.connect() as conn:
        # ============================================================
        # Organizations
        # ============================================================
        if "organizations" not in existing:
            conn.execute(text("""
                CREATE TABLE organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(500) NOT NULL,
                    aliases_json JSON DEFAULT '[]',
                    org_type VARCHAR(50),
                    parent_org_id INTEGER REFERENCES organizations(id),
                    website VARCHAR(500),
                    domain VARCHAR(200),
                    address_line VARCHAR(500),
                    city VARCHAR(200),
                    state VARCHAR(100),
                    zip_code VARCHAR(20),
                    country VARCHAR(100) DEFAULT 'US',
                    geographic_scope VARCHAR(100),
                    description TEXT,
                    logo_url VARCHAR(500),
                    founded_year INTEGER,
                    source_url VARCHAR(500),
                    data_provenance VARCHAR(50) DEFAULT 'observed',
                    confidence REAL DEFAULT 1.0,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_org_name ON organizations(name)"))
            conn.execute(text("CREATE INDEX ix_org_type ON organizations(org_type)"))
            conn.execute(text("CREATE INDEX ix_org_domain ON organizations(domain)"))
            print("  Created: organizations")

        if "organization_aliases" not in existing:
            conn.execute(text("""
                CREATE TABLE organization_aliases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER NOT NULL REFERENCES organizations(id),
                    alias_name VARCHAR(500) NOT NULL,
                    alias_type VARCHAR(50),
                    effective_from DATETIME,
                    effective_to DATETIME,
                    source_url VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_orgalias_orgid ON organization_aliases(organization_id)"))
            print("  Created: organization_aliases")

        # ============================================================
        # Contacts
        # ============================================================
        if "contacts" not in existing:
            conn.execute(text("""
                CREATE TABLE contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER REFERENCES organizations(id),
                    name_first VARCHAR(200),
                    name_last VARCHAR(200),
                    name_display VARCHAR(400) NOT NULL,
                    title VARCHAR(300),
                    department VARCHAR(300),
                    role_type VARCHAR(50),
                    email VARCHAR(300),
                    phone VARCHAR(50),
                    source_url VARCHAR(500),
                    source_document VARCHAR(500),
                    retrieval_date DATETIME,
                    effective_from DATETIME,
                    effective_to DATETIME,
                    verification_status VARCHAR(30) DEFAULT 'source_reported',
                    confidence REAL DEFAULT 0.8,
                    data_provenance VARCHAR(50) DEFAULT 'observed',
                    is_current BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_contact_orgid ON contacts(organization_id)"))
            conn.execute(text("CREATE INDEX ix_contact_role ON contacts(role_type)"))
            conn.execute(text("CREATE INDEX ix_contact_name ON contacts(name_last, name_first)"))
            conn.execute(text("CREATE INDEX ix_contact_email ON contacts(email)"))
            print("  Created: contacts")

        if "opportunity_contact_links" not in existing:
            conn.execute(text("""
                CREATE TABLE opportunity_contact_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
                    contact_id INTEGER NOT NULL REFERENCES contacts(id),
                    role VARCHAR(50),
                    source_url VARCHAR(500),
                    effective_from DATETIME,
                    effective_to DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(opportunity_id, contact_id)
                )
            """))
            conn.execute(text("CREATE INDEX ix_ocl_oppid ON opportunity_contact_links(opportunity_id)"))
            conn.execute(text("CREATE INDEX ix_ocl_contactid ON opportunity_contact_links(contact_id)"))
            print("  Created: opportunity_contact_links")

        # ============================================================
        # Opportunity-Organization junction
        # ============================================================
        if "opportunity_organizations" not in existing:
            conn.execute(text("""
                CREATE TABLE opportunity_organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id INTEGER NOT NULL REFERENCES opportunities(id),
                    organization_id INTEGER NOT NULL REFERENCES organizations(id),
                    role VARCHAR(50) NOT NULL,
                    source_url VARCHAR(500),
                    effective_from DATETIME,
                    effective_to DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(opportunity_id, organization_id, role)
                )
            """))
            conn.execute(text("CREATE INDEX ix_oo_oppid ON opportunity_organizations(opportunity_id)"))
            conn.execute(text("CREATE INDEX ix_oo_orgid ON opportunity_organizations(organization_id)"))
            print("  Created: opportunity_organizations")

        # ============================================================
        # Community: Creator tokens
        # ============================================================
        if "creator_tokens" not in existing:
            conn.execute(text("""
                CREATE TABLE creator_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_hash VARCHAR(64) NOT NULL UNIQUE,
                    recovery_key_hash VARCHAR(64) UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    generation_count INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT 0
                )
            """))
            print("  Created: creator_tokens")

        # ============================================================
        # Strategies
        # ============================================================
        if "strategies" not in existing:
            conn.execute(text("""
                CREATE TABLE strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_hash VARCHAR(64) NOT NULL,
                    mode VARCHAR(30) NOT NULL,
                    title VARCHAR(500),
                    inputs_json JSON,
                    results_json JSON,
                    report_json JSON,
                    status VARCHAR(20) DEFAULT 'draft',
                    is_public BOOLEAN DEFAULT 0,
                    visibility_confirmed BOOLEAN DEFAULT 0,
                    version INTEGER DEFAULT 1,
                    tags_json JSON DEFAULT '[]',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME,
                    delete_confirmed_at DATETIME
                )
            """))
            conn.execute(text("CREATE INDEX ix_strategy_creator ON strategies(creator_hash)"))
            conn.execute(text("CREATE INDEX ix_strategy_status ON strategies(status)"))
            conn.execute(text("CREATE INDEX ix_strategy_public ON strategies(is_public, status)"))
            print("  Created: strategies")

        # ============================================================
        # Reports
        # ============================================================
        if "reports" not in existing:
            conn.execute(text("""
                CREATE TABLE reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_hash VARCHAR(64) NOT NULL,
                    title VARCHAR(500),
                    summary TEXT,
                    prompt TEXT NOT NULL,
                    plan_json JSON,
                    results_json JSON,
                    report_json JSON,
                    status VARCHAR(20) DEFAULT 'draft',
                    is_public BOOLEAN DEFAULT 0,
                    visibility_confirmed BOOLEAN DEFAULT 0,
                    version INTEGER DEFAULT 1,
                    tags_json JSON DEFAULT '[]',
                    filters_json JSON,
                    coverage_json JSON,
                    methodology TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME,
                    delete_confirmed_at DATETIME
                )
            """))
            conn.execute(text("CREATE INDEX ix_report_creator ON reports(creator_hash)"))
            conn.execute(text("CREATE INDEX ix_report_status ON reports(status)"))
            conn.execute(text("CREATE INDEX ix_report_public ON reports(is_public, status)"))
            print("  Created: reports")

        # ============================================================
        # Saved charts and views
        # ============================================================
        if "saved_charts" not in existing:
            conn.execute(text("""
                CREATE TABLE saved_charts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_hash VARCHAR(64) NOT NULL,
                    title VARCHAR(500),
                    chart_type VARCHAR(50),
                    config_json JSON,
                    data_query TEXT,
                    filters_json JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_chart_creator ON saved_charts(creator_hash)"))
            print("  Created: saved_charts")

        if "saved_views" not in existing:
            conn.execute(text("""
                CREATE TABLE saved_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_hash VARCHAR(64) NOT NULL,
                    title VARCHAR(500),
                    view_type VARCHAR(30),
                    config_json JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_view_creator ON saved_views(creator_hash)"))
            print("  Created: saved_views")

        # ============================================================
        # Abuse reports
        # ============================================================
        if "abuse_reports" not in existing:
            conn.execute(text("""
                CREATE TABLE abuse_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_type VARCHAR(30) NOT NULL,
                    item_id INTEGER NOT NULL,
                    reason TEXT,
                    reporter_ip_hash VARCHAR(64),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at DATETIME
                )
            """))
            print("  Created: abuse_reports")

        # ============================================================
        # Add organization_id to opportunities (if not exists)
        # ============================================================
        opp_cols = {c["name"] for c in insp.get_columns("opportunities")}
        if "organization_id" not in opp_cols:
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN organization_id INTEGER REFERENCES organizations(id)"))
            print("  Added: opportunities.organization_id")

        conn.commit()
        print("\nMigration v3 complete!")


if __name__ == "__main__":
    print("Running schema migration v3...")
    run_migration()
