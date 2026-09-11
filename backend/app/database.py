"""SQLAlchemy database engine and session management for PostgreSQL."""

import os
from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


# Database engine configuration: Dedicated PostgreSQL cluster
def _build_engine():
    import time
    from pathlib import Path
    db_url = settings.database_url
    if db_url and "postgresql" in db_url.lower():
        timeout_sec = 1 if ("127.0.0.1" in db_url or "localhost" in db_url) else 15
        connect_args = {"connect_timeout": timeout_sec}
        ssl_mode = getattr(settings, "db_ssl_mode", "require")
        if "supabase" in db_url.lower():
            ssl_mode = "require"
        if "sslmode" not in db_url and ssl_mode:
            connect_args["sslmode"] = ssl_mode

        pg_engine = create_engine(
            db_url,
            echo=False,
            pool_size=getattr(settings, "db_pool_size", 5),
            max_overflow=getattr(settings, "db_max_overflow", 5),
            pool_timeout=getattr(settings, "db_pool_timeout", 15),
            pool_pre_ping=True,
            pool_recycle=getattr(settings, "db_pool_recycle", 120),
            connect_args=connect_args
        )
        try:
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[Database] Successfully connected to PostgreSQL cluster ({db_url.split('@')[-1] if '@' in db_url else 'localhost'})")
        except Exception as e:
            print(f"[Database Warning] Initial PostgreSQL ping had exception ({e}), pool_pre_ping will retry on demand.")
        return pg_engine

    # Fallback to local SQLite database in dev/offline testing only
    sqlite_path = Path(__file__).parent.parent / "data" / "nyserda.db"
    if not sqlite_path.exists() or sqlite_path.stat().st_size == 0:
        archive_path = Path(__file__).parent.parent / "data" / "archive_sqlite" / "nyserda.db"
        if archive_path.exists() and archive_path.stat().st_size > 0:
            import shutil
            shutil.copyfile(archive_path, sqlite_path)

    sqlite_url = f"sqlite:///{sqlite_path.resolve()}"
    return create_engine(
        sqlite_url,
        echo=False,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

engine = _build_engine()

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in database if needed and ensure primary system admin exists."""
    from app.models import (
        opportunity, program, project, source, analysis, award,
        recipient, organization, community, user, result, proposal,
        contact, relationship, attribution, technology, opportunity_organization,
        policy, admin_email, news, interconnection, lab_facility, sec_form_d,
        scaleup_capital, procurement, der_market, university_ip, user_activity
    )  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Ensure any new columns exist in PostgreSQL or SQLite safely without failing the entire batch
    def _safe_migration(stmt: str):
        try:
            with engine.connect() as conn:
                conn.execute(text(stmt))
                conn.commit()
        except Exception:
            pass

    if engine.dialect.name == "postgresql":
        pg_stmts = [
            "ALTER TABLE recipients ADD COLUMN IF NOT EXISTS enrichment_source VARCHAR(200);",
            "ALTER TABLE recipients ADD COLUMN IF NOT EXISTS last_enriched_at TIMESTAMP;",
            "ALTER TABLE recipients ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE recipients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE technologies ADD COLUMN IF NOT EXISTS vector_type VARCHAR(32) DEFAULT 'hardware';",
            "ALTER TABLE technologies ADD COLUMN IF NOT EXISTS fuel_profile_json TEXT;",
            "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS address_line1 VARCHAR(300);",
            "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS address_line2 VARCHAR(200);",
            "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS postal_code VARCHAR(30);",
            "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS formatted_address VARCHAR(500);",
            "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS address_verification_status VARCHAR(50) DEFAULT 'verified';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ghost_member_id VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ghost_subscription_tier VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ghost_status VARCHAR(50) DEFAULT 'free';",
            # user_activity_logs expanded telemetry columns
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS anon_id VARCHAR(64);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS country VARCHAR(10);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS region VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS city VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS cf_ray VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS screen_resolution VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS viewport_size VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS client_timezone VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS language VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS browser VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS os VARCHAR(50);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS initial_referrer VARCHAR(255);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS utm_source VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS utm_medium VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS utm_campaign VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS utm_term VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS utm_content VARCHAR(100);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS page_title VARCHAR(255);",
            "ALTER TABLE user_activity_logs ADD COLUMN IF NOT EXISTS event_data TEXT;",
        ]
        for s in pg_stmts:
            _safe_migration(s)
    else:
        sqlite_cols = [
            ("users", "ghost_member_id", "TEXT"),
            ("users", "ghost_subscription_tier", "TEXT"),
            ("users", "ghost_status", "TEXT DEFAULT 'free'"),
            ("contacts", "address_line1", "TEXT"),
            ("contacts", "address_line2", "TEXT"),
            ("contacts", "postal_code", "TEXT"),
            ("contacts", "formatted_address", "TEXT"),
            ("contacts", "address_verification_status", "TEXT DEFAULT 'verified'"),
            ("opportunities", "eligible_applicant_types", "TEXT"),
            ("opportunities", "eligible_technology_areas", "TEXT"),
            ("opportunities", "eligible_sectors", "TEXT"),
            ("opportunities", "eligible_activity_types", "TEXT"),
            ("opportunities", "project_cost_min", "REAL"),
            ("opportunities", "project_cost_max", "REAL"),
            ("opportunities", "cost_share_mandatory", "INTEGER DEFAULT 0"),
            ("opportunities", "statutory_mandates", "TEXT"),
            ("opportunities", "priority_problem_statements", "TEXT"),
            ("opportunities", "scoring_rubric_weights", "TEXT"),
            ("opportunities", "proposal_requirements_summary", "TEXT"),
            ("opportunities", "teaming_partner_types_sought", "TEXT"),
            ("opportunities", "disadvantaged_community_priority", "INTEGER DEFAULT 0"),
            ("opportunities", "total_awarded", "REAL"),
            ("opportunities", "award_count_actual", "INTEGER"),
            ("opportunities", "funding_provenance", "TEXT"),
            ("user_activity_logs", "anon_id", "TEXT"),
            ("user_activity_logs", "country", "TEXT"),
            ("user_activity_logs", "region", "TEXT"),
            ("user_activity_logs", "city", "TEXT"),
            ("user_activity_logs", "postal_code", "TEXT"),
            ("user_activity_logs", "latitude", "REAL"),
            ("user_activity_logs", "longitude", "REAL"),
            ("user_activity_logs", "cf_ray", "TEXT"),
            ("user_activity_logs", "screen_resolution", "TEXT"),
            ("user_activity_logs", "viewport_size", "TEXT"),
            ("user_activity_logs", "client_timezone", "TEXT"),
            ("user_activity_logs", "language", "TEXT"),
            ("user_activity_logs", "browser", "TEXT"),
            ("user_activity_logs", "os", "TEXT"),
            ("user_activity_logs", "initial_referrer", "TEXT"),
            ("user_activity_logs", "utm_source", "TEXT"),
            ("user_activity_logs", "utm_medium", "TEXT"),
            ("user_activity_logs", "utm_campaign", "TEXT"),
            ("user_activity_logs", "utm_term", "TEXT"),
            ("user_activity_logs", "utm_content", "TEXT"),
            ("user_activity_logs", "page_title", "TEXT"),
            ("user_activity_logs", "event_data", "TEXT"),
        ]
        for tbl, col, typ in sqlite_cols:
            _safe_migration(f"ALTER TABLE {tbl} ADD COLUMN {col} {typ};")
        _safe_migration("ALTER TABLE programs ADD COLUMN organization_id INTEGER;")
    
    # Auto-seed primary system administrator

    try:
        from app.models.user import User
        from app.core.security import hash_password, generate_random_token
        admin_email_addr = (settings.admin_primary_email or "bowens@aixenergy.io").strip().lower()
        with SessionLocal() as session:
            admin_user = session.query(User).filter(User.email == admin_email_addr).first()
            if not admin_user:
                initial_pw = settings.admin_gmail_password or generate_random_token(16)
                admin_user = User(
                    email=admin_email_addr,
                    hashed_password=hash_password(initial_pw),
                    full_name=settings.admin_primary_name or "Brandon Owens",
                    organization_name="AIxEnergy / Energy Innovation Terminal",
                    role="admin",
                    tier="enterprise",
                    tier_status="active",
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                session.add(admin_user)
                session.commit()
            else:
                # Ensure admin privileges are up to date
                needs_update = False
                if admin_user.role != "admin":
                    admin_user.role = "admin"
                    needs_update = True
                if not admin_user.is_active:
                    admin_user.is_active = True
                    needs_update = True
                if not admin_user.full_name:
                    admin_user.full_name = "Brandon Owens"
                    needs_update = True
                if needs_update:
                    session.commit()
    except Exception as e:
        print(f"Warning during admin user auto-seeding: {e}")


def init_fts():
    """Create PostgreSQL GIN full-text search indexes or SQLite performance indexes safely."""
    def _safe_exec(conn, query_str):
        try:
            conn.execute(text(query_str))
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass

    if engine.dialect.name == "postgresql":
        with engine.connect() as conn:
            # Check if GIN index already exists to avoid redundant DDL scans on every boot
            existing = conn.execute(text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_opportunities_fts';")).scalar()
            if existing:
                return
            # PostgreSQL GIN indexes for fast full-text search
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_opportunities_fts ON opportunities 
                USING gin(to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(short_description, '') || ' ' || COALESCE(solicitation_number, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_awards_fts ON awards 
                USING gin(to_tsvector('english', COALESCE(recipient_name, '') || ' ' || COALESCE(project_title, '') || ' ' || COALESCE(project_abstract, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_recipients_fts ON recipients 
                USING gin(to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(primary_technology, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_proposals_fts ON proposals 
                USING gin(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(solicitation_number, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_artifacts_fts ON result_artifacts 
                USING gin(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(summary, '') || ' ' || COALESCE(recipient_name, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_reports_fts ON reports 
                USING gin(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(summary, '')));
            """)
            _safe_exec(conn, """
                CREATE INDEX IF NOT EXISTS idx_policy_standards_fts ON policy_standards 
                USING gin(to_tsvector('english', 
                    COALESCE(code_identifier, '') || ' ' || 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(short_title, '') || ' ' || 
                    COALESCE(executive_summary, '') || ' ' || 
                    COALESCE(compliance_mandate, '') || ' ' || 
                    COALESCE(commercial_friction_points, '')
                ));
            """)
            # Relational performance indexes
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_program_id ON opportunities (program_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_agency ON opportunities (agency);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities (status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_prog_status ON opportunities (program_id, status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_agency_prog ON opportunities (agency, program_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_jurisdiction ON opportunities (jurisdiction);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_is_historical ON opportunities (is_historical);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_year ON opportunities (year);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_total_funding ON opportunities (total_funding);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_cat_type_val ON opportunity_categories (category_type, category_value);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_cat_type_opp ON opportunity_categories (category_type, opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_cat_composite ON opportunity_categories (opportunity_id, category_type, category_value);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_rounds_opp_stat ON opportunity_rounds (opportunity_id, status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_rounds_due ON opportunity_rounds (due_date);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_restrict_opp_id ON opportunity_restrictions (opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_restrict_cat ON opportunity_restrictions (category);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_prog_focus_prog ON program_focus_areas (program_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_opp_id ON awards (opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_state ON awards (recipient_state);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_agency ON awards (agency);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_year ON awards (year);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_amount ON awards (award_amount);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_type ON awards (award_type);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_ext_id ON awards (external_award_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_start_date ON awards (start_date);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_recipient_lower ON awards (LOWER(recipient_name));")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_recip_year ON awards (recipient_name, year);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_lat_lng ON awards (latitude, longitude);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_opp_agency ON awards (opportunity_id, agency);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_state ON recipients (headquarters_state);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_funding ON recipients (total_funding_received);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_name_lower ON recipients (LOWER(name));")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_norm_name ON recipients (normalized_name);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_ny_based ON recipients (is_ny_based);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_type ON recipients (recipient_type);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_recipients_primary_tech ON recipients (primary_technology);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_artifacts_award_id ON result_artifacts (award_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_artifacts_opp_id ON result_artifacts (opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts (email);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_contacts_role_type ON contacts (role_type);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_contacts_email_status ON contacts (email_status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_contacts_org_id ON contacts (organization_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_contacts_tech_area ON contacts (technology_area);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_category ON policy_standards(category);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_jurisdiction ON policy_standards(jurisdiction_level, jurisdiction_state);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_status ON policy_standards(status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_tech_link_tech ON policy_technology_links(technology_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_opp_link_opp ON policy_opportunity_links(opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_policy_fuel_link_fuel ON policy_fuel_links(fuel_vector);")
            
            # Initialize core analytics summary views
            try:
                from app.database_views import views_sql
                for _, view_create_sql in views_sql.items():
                    _safe_exec(conn, view_create_sql)
            except Exception as e:
                print(f"[Database] View init note: {e}")
    elif engine.dialect.name == "sqlite":
        with engine.connect() as conn:
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_program_id ON opportunities (program_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_agency ON opportunities (agency);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities (status);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_opp_id ON awards (opportunity_id);")
            _safe_exec(conn, "CREATE INDEX IF NOT EXISTS idx_awards_state ON awards (recipient_state);")
