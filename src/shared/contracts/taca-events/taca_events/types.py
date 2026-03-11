"""
Event type constants and catalog.

Attributes on :class:`EventType` and :class:`RoutingKeys` are **not** defined
here manually.  They are auto-populated via
:meth:`~taca_events.pydantic_schemas.base.EventSchema.__init_subclass__`
whenever a concrete ``EventSchema`` subclass is *defined* (i.e. its module is
imported).  Import ``taca_events.pydantic_schemas`` (or any individual schema
module) before using these catalogs.
"""


class EventType:
    """
    Central catalog of all domain event types in the TACA system.

    Event naming convention: {aggregate}.{action}.v{version}

    Attributes are auto-populated when :class:`~taca_events.pydantic_schemas.base.EventSchema`
    subclasses are imported.  Each subclass calls :func:`setattr` on this class
    from its ``__init_subclass__`` hook, so there is a single source of truth:
    the ``event_type()`` classmethod on the schema itself.
    """

    @classmethod
    def all_events(cls) -> list[str]:
        """Get list of all event types."""
        return [
            value
            for name, value in vars(cls).items()
            if not name.startswith("_") and isinstance(value, str)
        ]

    @classmethod
    def get_aggregate_type(cls, event_type: str) -> str:
        """
        Extract aggregate type from event type.

        Example: "match.created.v1" -> "match"
        """
        return event_type.split(".")[0]

    @classmethod
    def get_action(cls, event_type: str) -> str:
        """
        Extract action from event type.

        Example: "match.created.v1" -> "created"
        """
        parts = event_type.split(".")
        if len(parts) >= 2:
            return parts[1]
        return ""

    @classmethod
    def get_version(cls, event_type: str) -> str:
        """
        Extract version from event type.

        Example: "match.created.v1" -> "v1"
        """
        parts = event_type.split(".")
        if len(parts) >= 3:
            return parts[-1]
        return "v1"

    @classmethod
    def get_routing_key(cls, event_type: str) -> str:
        """
        Get RabbitMQ routing key (without version suffix).

        Example: "match.created.v1" -> "match.created"
        """
        parts = event_type.split(".")
        if len(parts) >= 3 and parts[-1].startswith("v"):
            return ".".join(parts[:-1])
        return event_type


class RoutingKeys(EventType):
    """
    Central catalog of RabbitMQ routing keys for event publishing and subscription.

    Attributes are auto-populated alongside :class:`EventType` by the
    ``EventSchema.__init_subclass__`` hook.
    """
