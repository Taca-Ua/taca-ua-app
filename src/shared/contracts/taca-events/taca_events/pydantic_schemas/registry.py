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

from typing import TYPE_CHECKING, Dict, Optional, Type

if TYPE_CHECKING:
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

    # Avoid circular imports by deferring imports inside the function.
    from .matches import (
        MatchCommentAddedV1,
        MatchCommentDeletedV1,
        MatchCreatedV1,
        MatchDeletedV1,
        MatchLineupAssignedV1,
        MatchParticipantAddedV1,
        MatchParticipantRemovedV1,
        MatchResultUpdatedV1,
        MatchUpdatedV1,
    )
    from .modalities import (
        CourseCreatedV1,
        CourseDeletedV1,
        CourseUpdatedV1,
        ModalityCreatedV1,
        ModalityDeletedV1,
        ModalityTypeCreatedV1,
        ModalityTypeDeletedV1,
        ModalityTypeUpdatedV1,
        ModalityUpdatedV1,
        NucleoCreatedV1,
        NucleoDeletedV1,
        NucleoUpdatedV1,
        StaffCreatedV1,
        StaffDeletedV1,
        StaffUpdatedV1,
        StudentCreatedV1,
        StudentDeletedV1,
        StudentUpdatedV1,
        TeamCreatedV1,
        TeamDeletedV1,
        TeamPlayerAddedV1,
        TeamPlayerRemovedV1,
        TeamUpdatedV1,
    )
    from .tournaments import (
        TournamentCompetitorAddedV1,
        TournamentCompetitorDeletedV1,
        TournamentCreatedV1,
        TournamentDeletedV1,
        TournamentFinishedV1,
        TournamentUpdatedV1,
    )

    schemas = [
        # Match events
        MatchCreatedV1,
        MatchUpdatedV1,
        MatchDeletedV1,
        MatchParticipantAddedV1,
        MatchParticipantRemovedV1,
        MatchLineupAssignedV1,
        MatchCommentAddedV1,
        MatchCommentDeletedV1,
        MatchResultUpdatedV1,
        # Nucleo events
        NucleoCreatedV1,
        NucleoUpdatedV1,
        NucleoDeletedV1,
        # Course events
        CourseCreatedV1,
        CourseUpdatedV1,
        CourseDeletedV1,
        # ModalityType events
        ModalityTypeCreatedV1,
        ModalityTypeUpdatedV1,
        ModalityTypeDeletedV1,
        # Modality events
        ModalityCreatedV1,
        ModalityUpdatedV1,
        ModalityDeletedV1,
        # Student events
        StudentCreatedV1,
        StudentUpdatedV1,
        StudentDeletedV1,
        # Staff events
        StaffCreatedV1,
        StaffUpdatedV1,
        StaffDeletedV1,
        # Team events
        TeamCreatedV1,
        TeamUpdatedV1,
        TeamDeletedV1,
        TeamPlayerAddedV1,
        TeamPlayerRemovedV1,
        # Tournament events
        TournamentCreatedV1,
        TournamentUpdatedV1,
        TournamentDeletedV1,
        TournamentFinishedV1,
        TournamentCompetitorAddedV1,
        TournamentCompetitorDeletedV1,
    ]

    for schema_cls in schemas:
        EventRegistry.register(schema_cls.routing_key(), schema_cls)


# Run registration immediately on import.
_register_defaults()
