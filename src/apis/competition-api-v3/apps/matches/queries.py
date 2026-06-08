from django.db.models import Q, QuerySet

from .models import Match, MatchParticipant


def list_matches(
    status: str = None,
    modality_id: str = None,
    course_id: str = None,
    tournament_id: str = None,
    date_from: str = None,
    date_to: str = None,
    page_size: int = None,
    offset: int = None,
) -> QuerySet[Match]:

    queryset = Match.objects.all()

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

    if course_id is not None:
        queryset = queryset.filter(
            Q(participants__competitor__athlete__course_id=course_id)
            | Q(participants__competitor__team__course_id=course_id)
        ).distinct()

    return queryset


def get_match_by_id(match_id) -> QuerySet[Match]:
    queryset = Match.objects.filter(id=match_id)
    if not queryset.exists():
        return None

    return queryset


def get_match_participant_by_id(
    match_id, participant_id, admin_id: str = None
) -> QuerySet[MatchParticipant]:
    queryset = MatchParticipant.objects.filter(match_id=match_id, id=participant_id)
    if not queryset.exists():
        return None

    if admin_id:
        participant = queryset.first()
        admins_responsible = participant.competitor.entity.course.nucleus.admins.filter(
            id=admin_id
        ).exists()
        if not admins_responsible:
            raise PermissionError(
                "Admin does not have permission to view this participant's lineup"
            )

    return queryset
