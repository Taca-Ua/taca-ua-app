import datetime
from uuid import UUID

from apps.tournaments.service import tournament_format_match_result
from django.db import transaction

from .models import Match, MatchParticipant, MatchStatus


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

    if new_journey:
        journies = match.tournament.available_rounds
        match.journey = max(journies) + 1 if journies else 1
        match.save()

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
    match = Match.objects.get(id=match_id)

    match.delete()


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

    match.status = MatchStatus.FINISHED
    match.save()

    # call tournament engine to handle match result
    tournament_format_match_result(match)

    return match


@transaction.atomic
def match_add_comment(match_id: UUID, comment_text: str, admin_id: UUID) -> Match:
    match = Match.objects.get(id=match_id)
    match.comments.create(content=comment_text, author_id=admin_id)

    return match


@transaction.atomic
def match_delete_comment(match_id: UUID, comment_id: UUID) -> Match:
    match = Match.objects.get(id=match_id)

    match.comments.filter(id=comment_id).delete()
    return match


@transaction.atomic
def assign_lineup(
    match_id: UUID, participant_id: UUID, players: list[UUID], admin_id: UUID = None
) -> MatchParticipant:
    match = Match.objects.get(id=match_id)
    participant = match.participants.get(id=participant_id)

    if admin_id:
        admins_responsible = participant.competitor.entity.course.nucleus.admins.filter(
            id=admin_id
        ).exists()
        if not admins_responsible:
            raise PermissionError(
                "Admin does not have permission to edit this participant's lineup"
            )

    # Clear existing lineup
    participant.lineup.all().delete()

    # Create new lineup
    for player in players:
        participant.lineup.create(athlete_id=player)

    return participant


@transaction.atomic
def update_lineup(
    match_id: UUID, participant_id: UUID, players: list[dict], admin_id: UUID = None
) -> MatchParticipant:
    match = Match.objects.get(id=match_id)
    participant = match.participants.get(id=participant_id)

    if admin_id:
        admins_responsible = participant.competitor.entity.course.nucleus.admins.filter(
            id=admin_id
        ).exists()
        if not admins_responsible:
            raise PermissionError(
                "Admin does not have permission to edit this participant's lineup"
            )

    # Update lineup based on provided player data
    for player_data in players:
        player_id = player_data.get("player_id")
        jersey_number = player_data.get("jersey_number")
        is_starter = player_data.get("is_starter")

        player_lineup = participant.lineup.get(athlete_id=player_id)

        if jersey_number is not None:
            player_lineup.jersey_number = jersey_number
        if is_starter is not None:
            player_lineup.is_starter = is_starter
        player_lineup.save()

    return participant


@transaction.atomic
def assign_staff_to_lineup(
    match_id: UUID, participant_id: UUID, staff_ids: list[UUID], admin_id: UUID = None
) -> MatchParticipant:
    match = Match.objects.get(id=match_id)
    participant = match.participants.get(id=participant_id)

    if admin_id:
        admins_responsible = participant.competitor.entity.course.nucleus.admins.filter(
            id=admin_id
        ).exists()
        if not admins_responsible:
            raise PermissionError(
                "Admin does not have permission to edit this participant's lineup"
            )

    # Clear existing staff assignments
    participant.staff.all().delete()

    # Create new staff assignments
    for staff_id in staff_ids:
        participant.staff.create(staff_id=staff_id)

    return participant
