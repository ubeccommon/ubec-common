"""
UBEC Protocol - Routes Package
==============================

FastAPI route modules for the UBEC Protocol web interface.

Modules:
    - admin_routes: Admin dashboard, authentication, and management

This project uses the services of Claude and Anthropic PBC.
"""

from .admin_routes import router as admin_router

__all__ = ['admin_router']
