from uuid import UUID

from apps.admins.models import Admin
from django.db.models import Exists, OuterRef, Prefetch, Q, QuerySet

from .models import Match, MatchParticipant


def get_participants_for_match(
    match_id: UUID = None,
    context_admin_id: UUID = None,
    include_lineup: bool = False,
) -> QuerySet[MatchParticipant]:

    participants_qs = MatchParticipant.objects.select_related(
        "competitor__athlete__course__nucleus",
        "competitor__team__course__nucleus",
    )

    if match_id:
        participants_qs = participants_qs.filter(match_id=match_id)

    if include_lineup:
        participants_qs = participants_qs.prefetch_related(
            "lineup__athlete__course__nucleus",
            "staff__staff",
        )

    if context_admin_id:
        participants_qs = participants_qs.annotate(
            can_edit=Exists(
                Admin.objects.filter(
                    id=context_admin_id,
                    nucleos__in=OuterRef("competitor__athlete__course__nucleus_id"),
                )
            )
            | Exists(
                Admin.objects.filter(
                    id=context_admin_id,
                    nucleos__in=OuterRef("competitor__team__course__nucleus_id"),
                )
            )
        )

    return participants_qs


def get_matches_table(
    match_id: UUID = None,
    status: str = None,
    modality_id: str = None,
    course_id: str = None,
    nucleus_id: str = None,
    tournament_id: str = None,
    season_id: str = None,
    admin_id: UUID = None,
    date_from: str = None,
    date_to: str = None,
    athlete_id: str = None,
    team_id: str = None,
    *,
    context_admin_id: UUID = None,
    include_lineups: bool = False,
) -> QuerySet[Match]:

    queryset = Match.objects.all()

    # filters
    if match_id is not None:
        queryset = queryset.filter(id=match_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    if modality_id is not None:
        queryset = queryset.filter(tournament__modality_id=modality_id)

    if date_from is not None:
        queryset = queryset.filter(scheduled_time__gte=date_from)

    if date_to is not None:
        queryset = queryset.filter(scheduled_time__lte=date_to)

    if tournament_id is not None:
        queryset = queryset.filter(tournament_id=tournament_id)

    if season_id is not None:
        queryset = queryset.filter(tournament__season_id=season_id)

    if course_id is not None:
        queryset = queryset.filter(
            Q(participants__competitor__athlete__course_id=course_id)
            | Q(participants__competitor__team__course_id=course_id)
        ).distinct()

    if nucleus_id is not None:
        queryset = queryset.filter(
            Q(participants__competitor__athlete__course__nucleus_id=nucleus_id)
            | Q(participants__competitor__team__course__nucleus_id=nucleus_id)
        ).distinct()

    if admin_id is not None:
        queryset = queryset.filter(
            Q(participants__competitor__athlete__course__nucleus__admins__id=admin_id)
            | Q(participants__competitor__team__course__nucleus__admins__id=admin_id)
        ).distinct()

    if athlete_id is not None:
        queryset = queryset.filter(
            participants__competitor__athlete_id=athlete_id
        ).distinct()

    if team_id is not None:
        queryset = queryset.filter(participants__competitor__team_id=team_id).distinct()

    queryset = queryset.select_related("tournament").prefetch_related(
        Prefetch(
            "participants",
            queryset=get_participants_for_match(
                context_admin_id=context_admin_id, include_lineup=include_lineups
            ),
        )
    )

    return queryset


def get_match_by_id(
    match_id: UUID, *, context_admin_id: UUID = None, include_lineups: bool = False
) -> Match:

    match_qs = get_matches_table(
        context_admin_id=context_admin_id, include_lineups=include_lineups
    ).filter(id=match_id)

    return match_qs.get()


def get_match_participant_by_id(
    match_id: UUID, participant_id: UUID, context_admin_id: UUID = None
) -> MatchParticipant:
    participant = get_participants_for_match(
        match_id=match_id, include_lineup=True
    ).get(id=participant_id)

    if (
        context_admin_id
        and not participant.competitor.entity.course.nucleus.admins.filter(
            id=context_admin_id
        ).exists()
    ):
        raise ValueError("Admin does not have access to this participant")

    return participant
