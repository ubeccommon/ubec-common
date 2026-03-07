"""
Module: registry.py
Service: hub
Purpose: Service registry — centralised dependency management (Principle #3).
         All inter-module dependencies resolved here, not via direct imports.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

from typing import Any


class ServiceRegistry:
    """Lightweight synchronous service registry."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """Register a service instance by name."""
        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered.")
        self._services[name] = service

    def get(self, name: str) -> Any:
        """Retrieve a registered service by name."""
        if name not in self._services:
            raise KeyError(f"Service '{name}' is not registered.")
        return self._services[name]

    async def initialise(self) -> None:
        """Initialise all registered services that implement async setup."""
        for name, svc in self._services.items():
            if hasattr(svc, "setup"):
                await svc.setup()

    async def teardown(self) -> None:
        """Gracefully shut down all registered services."""
        for name, svc in self._services.items():
            if hasattr(svc, "teardown"):
                await svc.teardown()


registry = ServiceRegistry()
