"""
Module: activities
Service: hub (iot.ubec.network)
Purpose: Activity and ActivityField management.
         Activities define structured observation templates with typed fields.
         They are independent of observations — not all activities produce observations.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from activities.routes import router

__all__ = ["router"]
