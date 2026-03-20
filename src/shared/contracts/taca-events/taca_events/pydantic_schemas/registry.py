"""
EventRegistry – maps RabbitMQ routing keys to typed ``EventSchema`` classes.

The registry is populated automatically when this module is imported via
``_register_defaults()``.  Custom schemas can be added at runtime with
``EventRegistry.register()``.

Usage in a consumer::

    from taca_events.pydantic_schemas import EventRegistry, MatchCreatedV1
    from taca_events.types import RoutingKeys

    @rabbitmq_service.event_handler(RoutingKeys.MATCH_CREATED)
    def handle_match_created(raw_event: dict):
        event = EventRegistry.parse(RoutingKeys.MATCH_CREATED, raw_event)
        if not isinstance(event, MatchCreatedV1):
            return
        match_id = event.data.match_id
"""

from typing import Dict, Optional, Type

from .base import EventSchema


class EventRegistry:
    """
    Central registry mapping routing keys to ``EventSchema`` subclasses.

    The registry supports:

    * ``register(routing_key, schema_class)`` – manual registration
    * ``parse(routing_key, raw_data)`` – parse inner data dict into a typed
      ``EventSchema`` instance (applies ``upgrade()`` when needed)
    * ``get(routing_key)`` – look up the schema class for a routing key
    * ``list_keys()`` – enumerate all registered routing keys
    """

    _registry: Dict[str, Type["EventSchema"]] = {}

    @classmethod
    def register(cls, routing_key: str, schema_class: Type["EventSchema"]) -> None:
        """
        Register a schema class for the given routing key.

        Args:
            routing_key: RabbitMQ routing key, e.g. ``'match.created'``.
            schema_class: ``EventSchema`` subclass to associate with the key.
        """
        cls._registry[routing_key] = schema_class

    @classmethod
    def get(cls, routing_key: str) -> Optional[Type["EventSchema"]]:
        """
        Return the schema class registered for *routing_key*, or ``None``.
        """
        return cls._registry.get(routing_key)

    @classmethod
    def parse(cls, routing_key: str, raw_data: dict) -> "EventSchema":
        """
        Parse a raw inner-data dict (received by a RabbitMQ handler) into a
        typed ``EventSchema`` instance.

        Steps:

        1. Look up the schema class for *routing_key*.
        2. Call ``schema_class.upgrade(raw_data)`` for schema-evolution support.
        3. Delegate to ``schema_class.from_data(upgraded_data)``.

        Args:
            routing_key: The event routing key, e.g. ``'match.created'``.
            raw_data: Inner ``data`` dict as delivered to the handler.

        Returns:
            A typed ``EventSchema`` subclass instance.

        Raises:
            KeyError: If no schema is registered for *routing_key*.
            pydantic.ValidationError: If *raw_data* fails schema validation.
        """
        schema_class = cls._registry.get(routing_key)
        if schema_class is None:
            raise KeyError(
                f"No schema registered for routing key '{routing_key}'. "
                f"Registered keys: {sorted(cls._registry.keys())}"
            )
        upgraded = schema_class.upgrade(raw_data)
        return schema_class.from_data(upgraded)

    @classmethod
    def list_keys(cls) -> list:
        """Return a sorted list of all registered routing keys."""
        return sorted(cls._registry.keys())


# --------------------------------------------------------------------------- #
# Auto-registration of built-in schemas
# --------------------------------------------------------------------------- #


def _register_defaults() -> None:
    """Register all built-in TACA event schemas with the ``EventRegistry``."""

    for schema_cls in EventSchema.__subclasses__():
        EventRegistry.register(schema_cls.routing_key(), schema_cls)


# Run registration immediately on import.
_register_defaults()
