"""
Module: observations
Service: hub (iot.ubec.network)
Purpose: Observation and ObservationResponse management.
         An Observation is a steward's phenomenological record tied to
         an Activity. Observations are independent entities — the Activities
         module has no knowledge of them.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from observations.routes import router

__all__ = ["router"]
