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
def update_match(
    match_id: UUID,
    location: str = None,
    start_time: datetime.datetime = None,
    status: str = None,
) -> Match:
    match = Match.objects.get(id=match_id)

    if location is not None:
        match.location = location

    if start_time is not None:
        match.scheduled_time = start_time

    if status is not None:
        match.status = status

    match.save()
    return match


@transaction.atomic
def delete_match(match_id: UUID) -> None:
    Match.objects.filter(id=match_id).delete()


@transaction.atomic
def publish_match_results(match_id: UUID, participant_results: list[dict]) -> Match:
    match = Match.objects.get(id=match_id)

    participant_results_dict = {
        result["participant_id"]: result for result in participant_results
    }

    for participant in match.participants.all():
        result = participant_results_dict.get(participant.id)
        if result:
            participant.score = result.get("score")
            participant.position = result.get("position")
            # participant.winner =
        participant.save()

    return match
