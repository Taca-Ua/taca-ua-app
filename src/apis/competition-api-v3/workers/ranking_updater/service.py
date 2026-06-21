import logging
from uuid import UUID

from apps.ranking.service import recompute_rankings
from apps.tournaments.models import TournamentStatus
from apps.tournaments.selectors import get_tournaments_table
from django.db import transaction

from .models import RankingRecomputationRequest

logger = logging.getLogger(__name__)


@transaction.atomic
def request_ranking_recomputation(
    season_id: UUID = None,
    modality_id: UUID = None,
    modality_type_id: UUID = None,
    tournament_id: UUID = None,
):
    """Creates a RankingRecomputationRequest entry to request a ranking recomputation for the given filters."""

    RankingRecomputationRequest.objects.create(
        season_id=season_id,
        modality_id=modality_id,
        modality_type_id=modality_type_id,
        tournament_id=tournament_id,
    )


@transaction.atomic
def handle_pending_recomputation_requests():
    """Handles pending ranking recomputation requests by processing them and emitting updated rankings events."""
    pending_requests = RankingRecomputationRequest.objects.filter(
        processed=False
    ).select_for_update()[:100]

    if not pending_requests:
        logger.info("No pending ranking recomputation requests found.")
        return

    # merge in to a list of tournaments ids
    tournament_ids = set()
    for request in pending_requests:
        tournament_ids.update(
            get_tournaments_table(
                status=TournamentStatus.FINISHED,  # only finished tournaments should be considered for ranking recomputation
                season_id=request.season_id,
                modality_id=request.modality_id,
                modality_type_id=request.modality_type_id,
                tournament_id=request.tournament_id,
            ).values_list("id", flat=True)
        )

    if not tournament_ids:
        return

    # process each tournament
    try:
        for tournament_id in tournament_ids:
            recompute_rankings(tournament_id=tournament_id)
    except Exception as e:
        logger.error(f"Error processing ranking recomputation requests: {e}")
        raise e

    logger.info(
        f"Processed [{len(pending_requests)}] ranking recomputation requests for [{len(tournament_ids)}] tournaments."
    )

    # mark processed requests
    for request in pending_requests:
        request.processed = True
        request.save()
