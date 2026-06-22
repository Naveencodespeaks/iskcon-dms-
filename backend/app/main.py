"""
Entry point for the FastAPI application.

This module creates the FastAPI app, configures middleware, mounts
all API routers (authentication, tenants, users, jobs, messages,
documents, search, whatsapp webhook) and exposes the ASGI callable
``app``.  It also provides startup and shutdown hooks for connecting
to external services if needed.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import engine
from .models.base import Base

from .auth.routes import router as auth_router
from .api.v1.tenants import router as tenant_router
from .api.v1.users import router as user_router
from .api.v1.jobs import router as job_router
from .api.v1.documents import router as document_router
from .api.v1.messages import router as message_router
from .api.v1.search import router as search_router
from .api.v1.roles import router as role_router
from .api.v1.assignments import router as assignment_router
from .api.v1.analytics import router as analytics_router
from .api.v1.escalations import router as escalation_router
from .integrations.whatsapp import router as whatsapp_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=settings.app_name)
    # Configure CORS to allow cross‑origin requests from frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Include routers
    app.include_router(auth_router)
    app.include_router(tenant_router)
    app.include_router(user_router)
    app.include_router(job_router)
    app.include_router(document_router)
    app.include_router(message_router)
    app.include_router(search_router)
    app.include_router(role_router)
    app.include_router(assignment_router)
    app.include_router(whatsapp_router)
    app.include_router(analytics_router)
    app.include_router(escalation_router)
    return app


app = create_app()


@app.on_event("startup")
async def create_tables_on_startup():
    """Create database tables on startup (convenience for deployment)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ensured (create_all done)")