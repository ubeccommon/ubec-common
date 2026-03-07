"""
Module: main.py
Service: erdpuls (erdpuls.ubec.network)
Purpose: Flagship physical Living Lab in Müllrose
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import logging
import json
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import settings
from registry import registry


# ── Logging ──────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter — never logs raw IPs or PII."""
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "level": record.levelname,
            "service": settings.SERVICE_NAME,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=settings.LOG_LEVEL, handlers=[handler])
logger = logging.getLogger(__name__)


# ── Application ───────────────────────────────────────────────────────

app = FastAPI(
    title="Erdpuls by UBEC",
    description="Flagship physical Living Lab in Müllrose",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Serve local design system fallback assets
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup() -> None:
    """Initialise service registry and validate required config on startup."""
    logger.warning("Starting %s in %s mode", settings.SERVICE_NAME, settings.SERVICE_ENV)
    await registry.initialise()


@app.on_event("shutdown")
async def shutdown() -> None:
    await registry.teardown()


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Basic liveness probe — used by Uptime Kuma and load balancers."""
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "env": settings.SERVICE_ENV,
    }


# ── Route registration ────────────────────────────────────────────────
# Import and include routers from api/ here. Example:
#
# from api.observations import router as observations_router
# app.include_router(observations_router, prefix="/api/v1/observations")
