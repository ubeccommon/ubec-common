"""
Module: config.py
Service: erdpuls
Purpose: Single source of truth for all configuration (Principle #8).
         All values loaded from environment — never hardcoded.
License: GNU AGPL v3.0

This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Platform settings — loaded from environment / .env file."""

    # Service identity
    SERVICE_NAME: str = "ubec-erdpuls"
    SERVICE_ENV: str = "development"
    LOG_LEVEL: str = "WARNING"

    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "ubec_erdpuls"
    DB_USER: str = "ubec_erdpuls_app"
    DB_PASSWORD: str  # REQUIRED — will raise on missing

    # Hub API
    HUB_API_URL: str = "https://iot.ubec.network"
    HUB_API_KEY: str  # REQUIRED

    # Stellar
    STELLAR_NETWORK: str = "testnet"
    STELLAR_HORIZON_URL: str = "https://horizon.stellar.org"

    # SSO (Phase 2)
    KEYCLOAK_URL: str = "https://auth.ubec.network"
    KEYCLOAK_REALM: str = "ubec-commons"
    KEYCLOAK_CLIENT_ID: str = "ubec-erdpuls"
    KEYCLOAK_CLIENT_SECRET: str = ""

    # Security
    SECRET_KEY: str  # REQUIRED
    ALLOWED_HOSTS: str = "localhost"
    CORS_ORIGINS: str = "https://ubec.network"

    # Analytics
    PLAUSIBLE_URL: str = "https://analytics.ubec.network"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
