"""
UBEC Protocol - Services Package
=================================

Shared services for the UBEC application.

Available services:
    email_service - Email notifications for applications

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

from services.email_service import (
    send_email,
    send_confirmation_email,
    send_admin_notification,
    send_status_update_email,
    is_email_configured
)

__all__ = [
    'send_email',
    'send_confirmation_email', 
    'send_admin_notification',
    'send_status_update_email',
    'is_email_configured'
]
