import logging

from django.db import transaction

from ..models import ProjectionUpdateRequest, ProjectionUpdateRequestTypes
from .rebuild_functions import (
    update_athletes_projections,
    update_general_rankings_projections,
    update_matches_projections,
    update_modality_rankings_projections,
    update_nucleus_projections,
    update_regulations_projections,
    update_seasons_projections,
    update_teams_projections,
    update_tournament_standings_projections,
    update_tournaments_projections,
)

logger = logging.getLogger(__name__)

PROJECTION_TYPE_HANDLERS: dict[str, callable] = {
    ProjectionUpdateRequestTypes.TEAM: update_teams_projections,
    ProjectionUpdateRequestTypes.ATHLETE: update_athletes_projections,
    ProjectionUpdateRequestTypes.MATCH: update_matches_projections,
    ProjectionUpdateRequestTypes.NUCLEO: update_nucleus_projections,
    ProjectionUpdateRequestTypes.GENERAL_RANKING: update_general_rankings_projections,
    ProjectionUpdateRequestTypes.MODALITY_RANKING: update_modality_rankings_projections,
    ProjectionUpdateRequestTypes.SEASON: update_seasons_projections,
    ProjectionUpdateRequestTypes.TOURNAMENT: update_tournaments_projections,
    ProjectionUpdateRequestTypes.TOURNAMENT_STANDING: update_tournament_standings_projections,
    ProjectionUpdateRequestTypes.REGULATION: update_regulations_projections,
}


@transaction.atomic
def request_projection_update(projection_type: str, payload: dict) -> None:
    """Create a new ProjectionUpdateRequest instance and save it to the database."""

    request = ProjectionUpdateRequest(
        projection_type=projection_type, payload=payload, processed=False
    )
    request.save()


@transaction.atomic
def handle_pending_projection_requests() -> None:
    """Handle pending projection update requests and update the projections accordingly."""

    # get all pending projection update requests
    pending_requests = ProjectionUpdateRequest.objects.filter(processed=False)

    for request in pending_requests:
        try:
            # get the handler function for the projection type
            handler_function = PROJECTION_TYPE_HANDLERS.get(request.projection_type)
            if handler_function:
                handler_function(**request.payload)
            else:
                logger.warning(
                    f"No handler function found for projection type {request.projection_type}"
                )

            # mark the request as processed
            request.processed = True
            request.save()
        except Exception as e:
            logger.error(
                f"Error processing projection update request {request.id}: {e}"
            )
