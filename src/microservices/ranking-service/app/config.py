"""
Configuration for Ranking Service.
"""

import os
from typing import Optional


class Config:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/taca_db",
    )

    # Security — shared internal token used by all microservices
    INTERNAL_API_TOKEN: str = os.getenv(
        "INTERNAL_API_TOKEN",
        "change-me-in-production",
    )

    # Domain service base URLs (Docker DNS names)
    MODALITIES_SERVICE_URL: str = os.getenv(
        "MODALITIES_SERVICE_URL",
        "http://modalities-service:8000",
    )
    TOURNAMENTS_SERVICE_URL: str = os.getenv(
        "TOURNAMENTS_SERVICE_URL",
        "http://tournaments-service:8000",
    )

    # Snapshot HTTP client settings
    SNAPSHOT_REQUEST_TIMEOUT: int = int(os.getenv("SNAPSHOT_REQUEST_TIMEOUT", "30"))
    SNAPSHOT_MAX_RETRIES: int = int(os.getenv("SNAPSHOT_MAX_RETRIES", "3"))

    @classmethod
    def get_snapshot_url(cls, service_name: str) -> Optional[str]:
        """Return the /internal/snapshot URL for the given service name."""
        urls = {
            "modalities": cls.MODALITIES_SERVICE_URL,
            "tournaments": cls.TOURNAMENTS_SERVICE_URL,
        }
        base = urls.get(service_name.lower())
        if base:
            return f"{base.rstrip('/')}/internal/snapshot"
        return None
