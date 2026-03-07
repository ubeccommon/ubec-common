"""
Module: auth/__init__.py
Service: hub (iot.ubec.network)
Purpose: Public API surface for the auth module.
         Import from here in main.py.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from auth.database import check_db_connection, get_db
from auth.dependencies import (
    CurrentSteward,
    get_current_steward,
    get_current_steward_optional,
    get_current_verified_steward,
    require_any_permission,
    require_any_role,
    require_permission,
    require_role,
)
from auth.routes import router
from auth.services import AuthService, PermissionService

__all__ = [
    # Router
    "router",
    # Database
    "get_db",
    "check_db_connection",
    # Dependencies
    "CurrentSteward",
    "get_current_steward",
    "get_current_steward_optional",
    "get_current_verified_steward",
    "require_permission",
    "require_any_permission",
    "require_role",
    "require_any_role",
    # Services
    "AuthService",
    "PermissionService",
]

__version__ = "1.0.0"
