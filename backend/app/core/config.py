"""
Configuration module for the AI Operations Copilot backend.

Loads settings from environment variables (and .env via docker).
Uses plain Python + os.getenv for maximum compatibility and reliability
in Docker without pydantic version conflicts.
"""

from __future__ import annotations
import os
from typing import Any


class Settings:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        # General
        self.app_name: str = os.getenv("APP_NAME", "AI Operations Copilot")
        self.env: str = os.getenv("ENV", "development")

        # Database
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@db:5432/copilot",
        )

        # Redis
        self.redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

        # Qdrant
        self.qdrant_url: str = os.getenv("QDRANT_URL", "http://qdrant:6333")

        # Celery
        self.celery_broker_url: str = os.getenv(
            "CELERY_BROKER_URL", "redis://redis:6379/1"
        )
        self.celery_result_backend: str = os.getenv(
            "CELERY_RESULT_BACKEND", "redis://redis:6379/2"
        )

        # JWT / Security
        self.secret_key: str = os.getenv("SECRET_KEY", "CHANGEME_SUPER_SECRET")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.refresh_token_expire_minutes: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080")
        )

        # WhatsApp
        self.whatsapp_verify_token: str = os.getenv(
            "WHATSAPP_VERIFY_TOKEN", "wh_verify_token_local"
        )
        self.whatsapp_access_token: str = os.getenv(
            "WHATSAPP_ACCESS_TOKEN", "wh_access_token_local"
        )


# Global singleton
settings = Settings()