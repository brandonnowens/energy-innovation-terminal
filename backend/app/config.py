"""Application configuration via environment variables."""

import os
from typing import Any
from pathlib import Path
from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).parent.parent.resolve()
_DEFAULT_DATA_DIR = _BACKEND_DIR / "data"
_DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DEFAULT_POSTGRES_URL = "postgresql+psycopg2://postgres.muihufwteznnncvwqovz:AtWkDzYsICn5axnw@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require"



from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment & Logging
    environment: str = "production"  # development, staging, production
    log_level: str = "INFO"

    # Database: Dedicated PostgreSQL cluster
    database_url: str = _DEFAULT_POSTGRES_URL
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_timeout: int = 15
    db_pool_recycle: int = 120
    db_ssl_mode: str = "require"  # disable, allow, prefer, require, verify-ca, verify-full

    # Background automated data pipelines & schedulers
    enable_background_schedulers: bool = False

    # CORS configuration for cloud hosting
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,https://terminal.aixenergy.io,https://aixenergy.io,https://energy-innovation-terminal.bowens-b7b.workers.dev,*"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed list of allowed CORS origins."""
        if not self.cors_origins or self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> str:
        url = str(v) if v else ""
        if not url or url.strip() == "":
            url = _DEFAULT_POSTGRES_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if "postgres@" in url and "postgres:postgres@" not in url:
            url = url.replace("postgres@", "postgres:postgres@", 1)
        return url

    # LLM Provider - Default to OpenAI for full intelligent synthesis across all features
    llm_provider: str = "openai"  # gemini, openai, anthropic, none
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Tavus.io Conversational Video
    tavus_api_key: str = ""
    tavus_replica_id: str = "read903b2a48"  # Brandon Owens April 14 2026 (Phoenix-4 CVI)
    tavus_persona_id: str = "p8c4fc7f28ac"  # Energy Innovation Terminal PAL (Ultra Low-Latency & Low-Token)

    # Socrata
    socrata_app_token: str = ""

    # Auth & Security
    jwt_secret_key: str = "energysignal-jwt-secret-key-2026-secure-token"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    public_benefit_mode: bool = True  # All users have 100% full free access to all intelligence features

    # Ghost.org Membership & Subscription Integration
    ghost_api_url: str = "https://aixenergy.io"
    ghost_admin_api_key: str = ""
    ghost_webhook_secret: str = ""

    # Platform Brand, Publisher & Citation Constants
    platform_name: str = "Energy Innovation Terminal"
    database_name: str = "U.S. Energy Innovation Database"
    company_name: str = "Clean Energy Research, LLC"
    platform_url: str = "https://terminal.aixenergy.io"
    citation_apa: str = "Owens, B. N. (2026). U.S. Energy Innovation Database (Version 3.5.0) [Data set and software]. Clean Energy Research, LLC. https://terminal.aixenergy.io"
    citation_bibtex: str = """@misc{owens2026energyinnovation,
  author = {Brandon N. Owens},
  title = {U.S. Energy Innovation Database},
  year = {2026},
  publisher = {Clean Energy Research, LLC},
  url = {https://terminal.aixenergy.io},
  note = {Multi-agency cross-jurisdictional intelligence covering 56,413 awards, $104.16B capital, and 140+ federal & state utilities}
}"""

    # System Admin & Gmail Outreach Integration
    admin_primary_email: str = "bowens@aixenergy.io"
    admin_primary_name: str = "Brandon Owens"
    admin_gmail_user: str = "bowens@aixenergy.io"
    admin_gmail_password: str = ""
    admin_smtp_host: str = "smtp.gmail.com"
    admin_smtp_port: int = 587
    admin_smtp_use_tls: bool = True
    admin_imap_host: str = "imap.gmail.com"
    admin_imap_port: int = 993
    admin_imap_use_ssl: bool = True
    admin_email_display_name: str = "Brandon Owens | Clean Energy Research, LLC"
    admin_email_default_footer: str = (
        "--\n"
        "Brandon N. Owens\n"
        "Clean Energy Research, LLC | Energy Innovation Terminal\n"
        "bowens@aixenergy.io | https://terminal.aixenergy.io\n"
        "U.S. Energy Innovation Database"
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Data directory
    data_dir: str = "./data"

    # NYSERDA API
    nyserda_funding_api_url: str = (
        "https://www.nyserda.ny.gov/rapi/fundingopportunitiesapi/"
        "getfundingopportunities?dataSourceId=a8166835-baba-4c2b-843d-c55e4583f19a"
    )
    nyserda_base_url: str = "https://www.nyserda.ny.gov"
    nyserda_portal_url: str = "https://portal.nyserda.ny.gov"

    # Socrata endpoints
    socrata_base_url: str = "https://data.ny.gov"
    socrata_rd_dataset: str = "7xzk-zyk5"
    socrata_renewables_dataset: str = "dprp-55ye"
    socrata_solar_dataset: str = "3x8r-34rs"
    socrata_storage_dataset: str = "ugya-enpy"

    # Grants.gov
    grants_gov_api_url: str = "https://api.grants.gov"
    grants_gov_api_key: str = ""  # Optional, for Simpler Grants API
    grants_gov_categories: str = "EN,ENV,ST"  # Energy, Environment, Science & Tech

    # SAM.gov  
    sam_gov_api_key: str = ""  # Optional

    # Target agencies for ingestion
    target_agencies: str = "NYSERDA,DOE,DOE-EERE,DOE-ARPAE,EPA,NSF"

    # Rate limiting
    request_delay_seconds: float = 0.5  # Between requests to same domain
    socrata_page_size: int = 1000

    # Grants.gov API
    target_agencies: str = "DOE,DOE-EERE,DOE-ARPAE,EPA,NSF"
    grants_gov_categories: str = "EN,ENV,ST"

    model_config = {
        "env_file": [str(_BACKEND_DIR.parent / ".env"), str(_BACKEND_DIR / ".env"), ".env"],
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @property
    def data_path(self) -> Path:
        """Resolved data directory path."""
        p = Path(self.data_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def documents_path(self) -> Path:
        """Path for downloaded documents."""
        p = self.data_path / "documents"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def snapshots_path(self) -> Path:
        """Path for page snapshots."""
        p = self.data_path / "snapshots"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def is_postgres(self) -> bool:
        """Check if configured database is PostgreSQL."""
        return "postgresql" in self.database_url.lower()


settings = Settings()

