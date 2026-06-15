import datetime
from uuid import UUID

from apps.tournaments.service import tournament_format_match_result
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import (
    MatchCommentAddedV1,
    MatchCommentDeletedV1,
    MatchCreatedV1,
    MatchDeletedV1,
    MatchLineupAssignedV1,
    MatchResultUpdatedV1,
    MatchUpdatedV1,
)
from taca_events.pydantic_schemas.matches import (
    LineupPlayerData,
    MatchCommentAddedData,
    MatchCommentDeletedData,
    MatchCreatedData,
    MatchDeletedData,
    MatchLineupAssignedData,
    MatchParticipantData,
    MatchResultEntryData,
    MatchResultUpdatedData,
    MatchUpdatedData,
)

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

    # Create match participants
    for competitor_id in participants:
        MatchParticipant.objects.create(
            match=match,
            competitor_id=competitor_id,
        )

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchCreatedV1.create(
            aggregate_id=match.id,
            data=MatchCreatedData(
                match_id=match.id,
                tournament_id=match.tournament.id,
                location=match.location,
                status=match.status,
                start_time=(
                    match.scheduled_time.isoformat() if match.scheduled_time else None
                ),
                journey=match.journey,
                participants=[
                    MatchParticipantData(participant_id=participant.id)
                    for participant in match.participants.all()
                ],
            ),
        ),
        aggregate_id=match.id,
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

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchUpdatedV1.create(
            aggregate_id=match.id,
            data=MatchUpdatedData(
                match_id=match.id,
                location=match.location,
                start_time=(
                    match.scheduled_time.isoformat() if match.scheduled_time else None
                ),
                status=match.status,
            ),
        ),
        aggregate_id=match.id,
    )

    return match


@transaction.atomic
def delete_match(match_id: UUID) -> None:
    match = Match.objects.get(id=match_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchDeletedV1.create(
            aggregate_id=match.id,
            data=MatchDeletedData(
                match_id=match.id,
                tournament_id=match.tournament.id,
            ),
        ),
        aggregate_id=match.id,
    )

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

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchResultUpdatedV1.create(
            aggregate_id=match.id,
            data=MatchResultUpdatedData(
                match_id=match.id,
                tournament_id=match.tournament.id,
                results=[
                    MatchResultEntryData(
                        participant_id=participant.id,
                        score=participant.score,
                        position=participant.position,
                    )
                    for participant in match.participants.all()
                ],
            ),
        ),
        aggregate_id=match.id,
    )

    return match


@transaction.atomic
def match_add_comment(match_id: UUID, comment_text: str, admin_id: UUID) -> Match:
    match = Match.objects.get(id=match_id)
    match.comments.create(content=comment_text, author_id=admin_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchCommentAddedV1.create(
            aggregate_id=match.id,
            data=MatchCommentAddedData(
                comment_id=match.comments.last().id,
                match_id=match.id,
                message=comment_text,
            ),
        ),
        aggregate_id=match.id,
    )
    return match


@transaction.atomic
def match_delete_comment(match_id: UUID, comment_id: UUID) -> Match:
    match = Match.objects.get(id=match_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchCommentDeletedV1.create(
            aggregate_id=match.id,
            data=MatchCommentDeletedData(
                comment_id=comment_id,
                match_id=match.id,
            ),
        ),
        aggregate_id=match.id,
    )

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

    # emit event to OutboxTable
    emit_schema_event(
        event=MatchLineupAssignedV1.create(
            aggregate_id=participant.id,
            data=MatchLineupAssignedData(
                match_id=match.id,
                team_id=participant.competitor.id,
                lineup=[
                    LineupPlayerData(player_id=player.match_participant.id)
                    for player in participant.lineup.all()
                ],
            ),
        ),
        aggregate_id=participant.id,
    )

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
