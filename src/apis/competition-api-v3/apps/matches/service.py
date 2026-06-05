import datetime
from uuid import UUID

from django.db import transaction

from .models import Match, MatchParticipant


@transaction.atomic
def create_match(
    tournament_id: UUID,
    participants: list[dict],
    location: str = None,
    start_time: datetime.datetime = None,
    journey=None,
    new_journey=False,
) -> Match:

    # Create the match
    match = Match.objects.create(
        tournament_id=tournament_id,
        location=location,
        scheduled_time=start_time,
        journey=journey,
    )

    # Create match participants
    for competitor_id in participants:
        MatchParticipant.objects.create(
            match=match,
            competitor_id=competitor_id,
        )

    return match


@transaction.atomic
def update_match(match_id, data) -> Match:
    # Logic to update a match and its related entities (participants, lineups, etc.)
    # This is a placeholder for the actual implementation
    pass


@transaction.atomic
def delete_match(match_id) -> None:
    Match.objects.filter(id=match_id).delete()
