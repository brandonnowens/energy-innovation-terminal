from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings

# Determine frontend static dist directory (local dev and Docker container paths)
_CANDIDATE_DIST_PATHS = [
    Path("/app/frontend/dist"),
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
    Path(__file__).resolve().parent.parent / "frontend" / "dist",
    Path("frontend/dist").resolve(),
]
_FRONTEND_DIST_DIR: Path | None = None
for p in _CANDIDATE_DIST_PATHS:
    if p.exists() and (p / "index.html").is_file():
        _FRONTEND_DIST_DIR = p
        break


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern asynchronous application lifecycle manager."""
    # ── Startup Phase ──
    from app.database import init_db, init_fts, SessionLocal, engine
    from app.services.news_service import start_daily_news_scheduler
    from app.engine.analyzer import get_cached_opportunities
    from app.services.ingestion.orchestrator import start_scheduler

    try:
        init_db()
        init_fts()
    except Exception as e:
        print(f"[Lifespan Startup Warning] DB/FTS Init: {e}")

    try:
        import gc
        with SessionLocal() as db:
            get_cached_opportunities(db)
        from app.engine.daily_digest import warm_digest_cache
        warm_digest_cache()
        gc.collect()
    except Exception as e:
        print(f"[Lifespan Startup Warning] Opportunity & Digest Cache Warm: {e}")

    # Background automated data schedulers (opt-in for dedicated worker nodes)
    if getattr(settings, "enable_background_schedulers", False):
        try:
            start_daily_news_scheduler()
            print("[Lifespan] Daily News Scheduler started.")
        except Exception as e:
            print(f"[Lifespan Startup Warning] News Scheduler: {e}")

        try:
            start_scheduler(60)
            print("[Lifespan] Ingestion Pipeline Scheduler started (60m).")
        except Exception as e:
            print(f"[Lifespan Startup Warning] Ingestion Scheduler: {e}")
    else:
        print("[Lifespan] Background schedulers disabled on API web node to conserve memory (ENABLE_BACKGROUND_SCHEDULERS=false).")

    yield

    # ── Shutdown Phase ──
    try:
        engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="Energy Innovation Terminal API",
    description=(
        "Energy Innovation Terminal - AI Clean Energy Grant Matching & Capital Intelligence API indexing "
        "public funding solicitations and awards across DOE, CEC, MassCEC, ARPA-E, NSF, and utilities."
    ),
    version="3.5.0",
    lifespan=lifespan,
    docs_url="/docs" if getattr(settings, "environment", "") == "development" else None,
    redoc_url="/redoc" if getattr(settings, "environment", "") == "development" else None,
    openapi_url="/openapi.json" if getattr(settings, "environment", "") == "development" else None,
)

# CORS for local and cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security, SEO, Observability & Compression middleware
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, HttpCacheControlMiddleware, ObservabilityMiddleware
from app.middleware.seo_prerender import SeoPrerenderMiddleware
from app.api.seo import router as seo_router

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(HttpCacheControlMiddleware)
app.add_middleware(RateLimitMiddleware, default_rpm=120, contact_rpm=10, export_rpm=20)
app.add_middleware(SeoPrerenderMiddleware)

# Mount SEO and Sitemaps at root
app.include_router(seo_router)

# Mount AI Chat copilot
from app.api.chat import router as chat_router
app.include_router(chat_router, prefix="/api/chat", tags=["AI Copilot"])


# Mount V1 Canonical Intelligence and Control Layer
from app.api.v1 import v1_router
app.include_router(v1_router, prefix="/api/v1", tags=["V1 Canonical Intelligence API"])

# Mount core API routes (100% backward compatible)
from app.api.analyze import router as analyze_router
from app.api.opportunities import router as opportunities_router
from app.api.system import router as system_router
from app.api.agencies import router as agencies_router
from app.api.trends import router as trends_router
from app.api.auth import router as auth_router
from app.api.ghost_webhook import router as ghost_router
from app.api.pdf_report import router as pdf_router
from app.api.relationships import router as relationships_router
from app.api.organizations import router as orgs_router
from app.api.contacts import router as contacts_router
from app.api.community import router as community_router
from app.api.strategy import router as strategy_router
from app.api.reports import router as reports_router
from app.api.charts import router as charts_router
from app.api.awards import router as awards_router
from app.api.network import router as network_router
from app.api.sankey import router as sankey_router
from app.api.results import router as results_router
from app.api.proposals import router as proposals_router
from app.api.artifacts import router as artifacts_router
from app.api.attributions import router as attributions_router
from app.api.linkages import router as linkages_router
from app.api.tech_reference import router as tech_reference_router
from app.api.policies import router as policies_router
from app.api.chat import router as chat_router
from app.api.tavus import router as tavus_router
from app.api.admin_email import router as admin_email_router
from app.api.news import router as news_router
from app.api.capital_intelligence import router as capital_intelligence_router
from app.api.forecasting import router as forecasting_router
from app.api.foa_shredder import router as foa_shredder_router
from app.api.alerts import router as alerts_router
from app.api.ira_calculator import router as ira_calculator_router
from app.api.ingestion import router as ingestion_router
from app.api.v1.digest import router as digest_router
from app.api.search import router as search_router
from app.api.telemetry import router as telemetry_router

app.include_router(telemetry_router, prefix="/api", tags=["Telemetry & Anonymous Visitor Analytics"])
app.include_router(search_router, prefix="/api", tags=["Universal Search"])
app.include_router(digest_router, prefix="/api", tags=["Daily Digest"])
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(opportunities_router, prefix="/api", tags=["Opportunities"])
app.include_router(system_router, prefix="/api", tags=["System"])
app.include_router(agencies_router, prefix="/api", tags=["Agencies"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(ghost_router, prefix="/api", tags=["Ghost Membership Integration"])
app.include_router(pdf_router, prefix="/api", tags=["PDF Report"])
app.include_router(relationships_router, prefix="/api", tags=["Relationships"])
app.include_router(trends_router)
app.include_router(orgs_router, prefix="/api", tags=["Organizations"])
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
app.include_router(community_router, prefix="/api", tags=["Community"])
app.include_router(strategy_router, prefix="/api", tags=["Strategy"])
app.include_router(reports_router, prefix="/api", tags=["Reports"])
app.include_router(charts_router, prefix="/api", tags=["Charts"])
app.include_router(awards_router, prefix="/api", tags=["Awards"])
app.include_router(network_router, prefix="/api", tags=["Network"])
app.include_router(sankey_router, prefix="/api", tags=["Sankey"])
app.include_router(results_router, prefix="/api", tags=["Results & Outcomes"])
app.include_router(proposals_router, prefix="/api", tags=["Winning Proposals"])
app.include_router(artifacts_router, prefix="/api", tags=["Artifacts & Downloads"])
app.include_router(attributions_router, prefix="/api", tags=["Venture & Patents"])
app.include_router(linkages_router, prefix="/api", tags=["Innovation Linkages"])
app.include_router(tech_reference_router, prefix="/api", tags=["Technology Reference"])
app.include_router(policies_router, prefix="/api", tags=["Policy, Codes & Standards"])
app.include_router(chat_router, prefix="/api", tags=["VP of Innovation Chat"])
app.include_router(tavus_router, prefix="/api", tags=["Tavus Video Advisor"])
app.include_router(admin_email_router, prefix="/api", tags=["Admin Email Hub"])
app.include_router(news_router, prefix="/api", tags=["Energy Innovation News Ticker"])
app.include_router(capital_intelligence_router, prefix="/api", tags=["Capital Intelligence & Infrastructure"])
app.include_router(forecasting_router, prefix="/api/forecasting", tags=["Predictive Release Forecasting"])
app.include_router(foa_shredder_router, prefix="/api", tags=["AI FOA Shredder"])
app.include_router(alerts_router, prefix="/api", tags=["Real-Time Alerts & Radar"])
app.include_router(ira_calculator_router, prefix="/api", tags=["IRA Calculator"])
app.include_router(ingestion_router, prefix="/api", tags=["Data Ingestion & Orchestration"])


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health():
    """Liveness and readiness health probe for cloud container orchestrators."""
    from app.database import engine
    from sqlalchemy import text
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    status_code = "ok" if db_status == "healthy" else "degraded"
    return {
        "status": status_code,
        "service": "Energy Innovation Terminal API",
        "version": "3.5.0",
        "database": {
            "status": db_status,
            "dialect": getattr(engine.dialect, "name", "unknown")
        },
        "environment": getattr(settings, "environment", "production")
    }


# ── Production Static Assets & SPA Fallback Serving ──
if _FRONTEND_DIST_DIR and _FRONTEND_DIST_DIR.exists():
    _assets_dir = _FRONTEND_DIST_DIR / "assets"
    if _assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    _logos_dir = _FRONTEND_DIST_DIR / "logos"
    if _logos_dir.is_dir():
        app.mount("/logos", StaticFiles(directory=str(_logos_dir)), name="logos")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_frontend(request: Request, full_path: str):
    """Serve built frontend static files and handle Single Page Application (SPA) client-side routing."""
    # Never intercept API, OpenAPI documentation, or SEO endpoints
    if (
        full_path.startswith("api/")
        or full_path in ("docs", "openapi.json", "redoc")
        or full_path.startswith("feed/")
    ):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    if _FRONTEND_DIST_DIR and _FRONTEND_DIST_DIR.exists():
        # Check if requested static file exists in dist (e.g., favicon.png, icons.svg)
        target_file = _FRONTEND_DIST_DIR / full_path
        if target_file.is_file():
            return FileResponse(target_file)

        # Fallback to index.html for React client-side routing
        index_file = _FRONTEND_DIST_DIR / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend build not found")

