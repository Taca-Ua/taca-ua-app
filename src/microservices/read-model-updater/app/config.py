"""
Configuration module for Read Model Updater Service.

Handles environment variables for:
- Database connection
- RabbitMQ connection
- Domain service URLs for snapshot endpoints
- Security tokens
"""

import os
from typing import Optional


class Config:
    """
    Centralized configuration for the Read Model Updater service.

    All environment variables should be defined here to avoid hardcoded values
    and provide a single source of truth for configuration.
    """

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/taca_db",
    )

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")

    # Domain Service URLs for Snapshot Fetching
    # These use Docker service name DNS resolution
    # Example: http://matches-service:8000
    MATCHES_SERVICE_URL: str = os.getenv(
        "MATCHES_SERVICE_URL",
        "http://matches-service:8000",
    )
    TOURNAMENT_SERVICE_URL: str = os.getenv(
        "TOURNAMENT_SERVICE_URL",
        "http://tournaments-service:8000",
    )
    MODALITIES_SERVICE_URL: str = os.getenv(
        "MODALITIES_SERVICE_URL",
        "http://modalities-service:8000",
    )
    RANKING_SERVICE_URL: str = os.getenv(
        "RANKING_SERVICE_URL",
        "http://ranking-service:8000",
    )

    # Security Configuration
    # Internal API token for securing rebuild endpoint
    INTERNAL_API_TOKEN: str = os.getenv(
        "INTERNAL_API_TOKEN",
        "change-me-in-production",
    )

    # Rebuild Configuration
    # Timeout for snapshot HTTP requests (in seconds)
    SNAPSHOT_REQUEST_TIMEOUT: int = int(os.getenv("SNAPSHOT_REQUEST_TIMEOUT", "30"))

    # Maximum retries for snapshot fetching
    SNAPSHOT_MAX_RETRIES: int = int(os.getenv("SNAPSHOT_MAX_RETRIES", "3"))

    @classmethod
    def validate(cls) -> None:
        """
        Validate critical configuration values.

        Raises:
            ValueError: If critical configuration is missing or invalid
        """
        if cls.INTERNAL_API_TOKEN == "change-me-in-production":
            # Log warning but don't fail - useful for development
            import warnings

            warnings.warn(
                "INTERNAL_API_TOKEN is using default value. "
                "Please set a secure token in production!"
            )

        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")

    @classmethod
    def get_snapshot_url(cls, service_name: str) -> Optional[str]:
        """
        Get the snapshot endpoint URL for a domain service.

        Args:
            service_name: Name of the domain service
                         ('matches', 'tournament', 'modalities', 'ranking')

        Returns:
            Full URL to the snapshot endpoint, or None if service not configured
        """
        service_urls = {
            "matches": cls.MATCHES_SERVICE_URL,
            "tournament": cls.TOURNAMENT_SERVICE_URL,
            "modalities": cls.MODALITIES_SERVICE_URL,
            "ranking": cls.RANKING_SERVICE_URL,
        }

        base_url = service_urls.get(service_name.lower())
        if base_url:
            # Ensure no trailing slash before appending endpoint path
            base_url = base_url.rstrip("/")
            return f"{base_url}/internal/snapshot"

        return None


# Validate configuration on module import
Config.validate()
