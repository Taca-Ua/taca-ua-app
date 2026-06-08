from uuid import UUID

from apps.admins.models import Admin
from django.db.models import Exists, OuterRef, Prefetch, QuerySet

from ..models import (
    Match,
    MatchParticipant,
    MatchParticipantAthleteLineup,
    MatchParticipantStaffAssignment,
)


def render_match_list(
    matches: QuerySet[Match] | Match,
    include_lineups: bool = False,
    admin_id: UUID | None = None,
) -> QuerySet[Match]:
    """Render a list of matches with summary information

    Args:
        matches: Match queryset or single Match instance
        include_lineups: Whether to include lineup data for participants
        admin_id: Optional admin ID to annotate can_edit field based on nucleus management
    """
    if isinstance(matches, Match):
        matches = Match.objects.filter(id=matches.id)

    matches = matches.select_related("tournament")

    lineups_prefetches = []
    if include_lineups:
        lineups_prefetches.append(
            Prefetch(
                "lineup",
                queryset=MatchParticipantAthleteLineup.objects.select_related(
                    "athlete__course__nucleus"
                ),
            )
        )
        lineups_prefetches.append(
            Prefetch(
                "staff",
                queryset=MatchParticipantStaffAssignment.objects.select_related(
                    "staff"
                ),
            )
        )

    # Build participant queryset with optional can_edit annotation
    participant_queryset = MatchParticipant.objects.select_related(
        "competitor__athlete__course__nucleus",
        "competitor__team__course__nucleus",
    ).prefetch_related(*lineups_prefetches)

    # Annotate can_edit based on admin managing the participant's nucleus
    if admin_id:
        can_edit_annotation = Exists(
            Admin.objects.filter(
                id=admin_id,
                nucleos__in=OuterRef("competitor__athlete__course__nucleus_id"),
            )
        ) | Exists(
            Admin.objects.filter(
                id=admin_id,
                nucleos__in=OuterRef("competitor__team__course__nucleus_id"),
            )
        )
        participant_queryset = participant_queryset.annotate(
            can_edit=can_edit_annotation
        )

    matches = matches.prefetch_related(
        Prefetch("participants", queryset=participant_queryset)
    )
    return matches


def render_match_detail(
    match: QuerySet[Match] | Match,
    include_lineups: bool = False,
    admin_id: UUID | None = None,
) -> QuerySet[Match]:
    """Render detailed match view with comments

    Args:
        match: Match queryset or single Match instance
        include_lineups: Whether to include lineup data for participants
        admin_id: Optional admin ID to annotate can_edit field based on nucleus management
    """
    if isinstance(match, Match):
        match = Match.objects.filter(id=match.id)

    match = render_match_list(match, include_lineups=include_lineups, admin_id=admin_id)

    match = match.prefetch_related("comments")

    return match


def render_match_participant(
    participant: QuerySet[MatchParticipant] | MatchParticipant,
) -> QuerySet[MatchParticipant]:

    if isinstance(participant, MatchParticipant):
        participant = MatchParticipant.objects.filter(id=participant.id)

    participant = participant.prefetch_related(
        Prefetch(
            "lineup",
            queryset=MatchParticipantAthleteLineup.objects.select_related(
                "athlete__course__nucleus"
            ),
        ),
        Prefetch(
            "staff",
            queryset=MatchParticipantStaffAssignment.objects.select_related("staff"),
        ),
    )

    return participant
