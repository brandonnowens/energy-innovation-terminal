"""
V1 Canonical API Router Aggregator.

Mounts all versioned intelligence, opportunities, organizations,
technologies, agent tools, and async job routers under /api/v1.
"""

from fastapi import APIRouter

from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.technologies import router as technologies_router
from app.api.v1.agents import router as agents_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.digest import router as digest_router

v1_router = APIRouter()

v1_router.include_router(intelligence_router)
v1_router.include_router(opportunities_router)
v1_router.include_router(organizations_router)
v1_router.include_router(technologies_router)
v1_router.include_router(agents_router)
v1_router.include_router(jobs_router)
v1_router.include_router(digest_router)

__all__ = ["v1_router"]

