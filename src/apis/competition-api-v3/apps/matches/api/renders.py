from django.db.models import Prefetch, QuerySet

from ..models import Match, MatchParticipant


def render_match_list(matches: QuerySet[Match] | Match) -> QuerySet[Match]:
    """Render a list of matches with summary information"""
    if isinstance(matches, Match):
        matches = Match.objects.filter(id=matches.id)

    matches = matches.select_related("tournament")

    matches = matches.prefetch_related(
        Prefetch(
            "participants",
            queryset=MatchParticipant.objects.select_related(
                "competitor__athlete__course__nucleus",
                "competitor__team__course__nucleus",
            ),
        )
    )
    return matches


def render_match_detail(match: QuerySet[Match] | Match) -> QuerySet[Match]:

    if isinstance(match, Match):
        match = Match.objects.filter(id=match.id)

    match = render_match_list(match)

    match = match.prefetch_related("comments")

    return match
