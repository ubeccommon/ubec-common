"""
Module: main.py
Service: hub (iot.ubec.network)
Purpose: Central REST API & IoT integration layer
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import settings
from registry import registry

# ── Auth module ───────────────────────────────────────────────────────────────
from auth import router as auth_router

from activities import router as activities_router

from observations import router as observations_router
# ── Logging ───────────────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter — never logs raw IPs or PII."""
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "level":     record.levelname,
            "service":   settings.SERVICE_NAME,
            "message":   record.getMessage(),
            "timestamp": self.formatTime(record),
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=settings.LOG_LEVEL, handlers=[handler])
logger = logging.getLogger(__name__)


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "UBEC Hub",
    description = "Central REST API & IoT integration layer — iot.ubec.network",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# Serve local design system fallback assets
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    logger.warning("Starting %s in %s mode", settings.SERVICE_NAME, settings.SERVICE_ENV)
    await registry.initialise()


@app.on_event("shutdown")
async def shutdown() -> None:
    await registry.teardown()


# ── System routes ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness probe — used by Uptime Kuma and nginx upstream checks."""
    return {
        "status":  "ok",
        "service": settings.SERVICE_NAME,
        "env":     settings.SERVICE_ENV,
    }


@app.get("/", tags=["system"])
async def root() -> dict:
    """Root endpoint — confirms the Hub is running."""
    return {
        "service":     "UBEC Hub",
        "description": "Central REST API & IoT integration layer",
        "docs":        "/docs",
        "health":      "/health",
    }


# ── Module routers ────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(activities_router)
app.include_router(observations_router)
# Future modules registered here:
# from observations import router as observations_router
# app.include_router(observations_router, prefix="/api/v1")
