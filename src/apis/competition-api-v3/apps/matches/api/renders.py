from django.db.models import Prefetch, QuerySet

from ..models import (
    Match,
    MatchParticipant,
    MatchParticipantAthleteLineup,
    MatchParticipantStaffAssignment,
)


def render_match_list(
    matches: QuerySet[Match] | Match, include_lineups: bool = False
) -> QuerySet[Match]:
    """Render a list of matches with summary information"""
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

    matches = matches.prefetch_related(
        Prefetch(
            "participants",
            queryset=MatchParticipant.objects.select_related(
                "competitor__athlete__course__nucleus",
                "competitor__team__course__nucleus",
            ).prefetch_related(*lineups_prefetches),
        )
    )
    return matches


def render_match_detail(
    match: QuerySet[Match] | Match, include_lineups: bool = False
) -> QuerySet[Match]:

    if isinstance(match, Match):
        match = Match.objects.filter(id=match.id)

    match = render_match_list(match, include_lineups=include_lineups)

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
