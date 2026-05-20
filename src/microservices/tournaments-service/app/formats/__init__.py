"""
Registry for tournament format engines.

Manages format engine instances and provides lookup by format name.
"""

from typing import Any, Dict, Optional

from .base import FormatEngine
from .free.free import FreeFormatEngine
from .league.league import LeagueFormatEngine


class FormatRegistry:
    """
    Registry for tournament format engines.

    Supports registration and lookup of format engines by name.
    """

    _engines: Dict[str, type] = {
        "free": FreeFormatEngine,
        "league": LeagueFormatEngine,
    }

    _instances: Dict[str, FormatEngine] = {}

    @classmethod
    def register(cls, format_name: str, engine_class: type) -> None:
        """
        Register a new format engine.

        Args:
            format_name: Name of the format (e.g., 'league', 'playoff')
            engine_class: FormatEngine subclass
        """
        cls._engines[format_name] = engine_class
        # Clear cached instance
        if format_name in cls._instances:
            del cls._instances[format_name]

    @classmethod
    def get_engine(
        cls, format_name: str, config: Optional[Dict[str, Any]] = None
    ) -> FormatEngine:
        """
        Get a format engine instance.

        Args:
            format_name: Name of the format
            config: Optional configuration dict to pass to engine

        Returns:
            FormatEngine instance

        Raises:
            ValueError: If format not registered
        """
        if format_name not in cls._engines:
            raise ValueError(
                f"Unknown tournament format: {format_name}. "
                f"Registered formats: {', '.join(cls._engines.keys())}"
            )

        engine_class = cls._engines[format_name]

        # If config provided, create new instance
        # Otherwise, use cached instance
        if config is not None:
            return engine_class(config)

        if format_name not in cls._instances:
            cls._instances[format_name] = engine_class()

        return cls._instances[format_name]

    @classmethod
    def is_valid_format(cls, format_name: str) -> bool:
        """Check if a format is registered."""
        return format_name in cls._engines

    @classmethod
    def list_formats(cls) -> list:
        """Return list of registered format names."""
        return list(cls._engines.keys())
