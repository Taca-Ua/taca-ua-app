from venv import logger

from apps.athletes.selectors import get_athletes_table
from apps.matches.selectors import get_matches_table
from apps.modalities.selectors import get_modalities_table
from apps.nucleus.selectors import get_nucleus_table
from apps.projections.service import (
    rebuild_general_ranking_projection,
    rebuild_match_projection,
    rebuild_modality_ranking_projection,
    rebuild_nucleo_projection,
    rebuild_regulation_projection,
    rebuild_season_projection,
    rebuild_student_projection,
    rebuild_team_projection,
    rebuild_tournament_projection,
    rebuild_tournament_standings_projection,
)
from apps.regulations.selectors import get_regulations_table
from apps.seasons.selectors import get_seasons_table
from apps.teams.selectors import get_teams_table
from apps.tournaments.selectors import get_tournaments_table
from django.db import transaction


@transaction.atomic
def update_teams_projections(
    team_id: str = None,
    course_id: str = None,
    modality_id: str = None,
    nucleus_id: str = None,
    athlete_id: str = None,
) -> None:
    """Update the projections for the teams based on the provided parameters."""
    args = {
        "team_id": team_id,
        "course_id": course_id,
        "modality_id": modality_id,
        "nucleus_id": nucleus_id,
        "athlete_id": athlete_id,
    }

    teams = get_teams_table(
        modality_id=modality_id,
        course_id=course_id,
        team_id=team_id,
        nucleus_id=nucleus_id,
        athlete_id=athlete_id,
    )

    if team_id is not None and teams.count() == 0:
        # team was deleted
        rebuild_team_projection(team_id=team_id)
        logger.info(
            f"Updated projections for team_id={team_id} (team deleted).", extra=args
        )
        return

    c = 0
    for team in teams:
        rebuild_team_projection(team_id=team.id)
        c += 1

    logger.info(f"Updated projections for [{c}] teams.", extra=args)


@transaction.atomic
def update_athletes_projections(
    athlete_id: str = None,
    course_id: str = None,
    nucleus_id: str = None,
    team_id: str = None,
) -> None:
    """Update the projections for the athletes based on the provided parameters."""
    args = {
        "athlete_id": athlete_id,
        "course_id": course_id,
        "nucleus_id": nucleus_id,
        "team_id": team_id,
    }

    athletes = get_athletes_table(
        course_id=course_id,
        athlete_id=athlete_id,
        nucleus_id=nucleus_id,
        team_id=team_id,
    )

    if athlete_id is not None and athletes.count() == 0:
        # athlete was deleted
        rebuild_student_projection(student_id=athlete_id)
        logger.info(
            f"Updated projections for athlete_id={athlete_id} (athlete deleted).",
            extra=args,
        )
        return

    c = 0
    for athlete in athletes:
        rebuild_student_projection(student_id=athlete.id)
        c += 1

    logger.info(f"Updated projections for [{c}] athletes.", extra=args)


@transaction.atomic
def update_matches_projections(
    match_id: str = None,
    tournament_id: str = None,
    modality_id: str = None,
    athlete_id: str = None,
    team_id: str = None,
) -> None:
    """Update the projections for the matches based on the provided parameters."""
    args = {
        "match_id": match_id,
        "tournament_id": tournament_id,
        "modality_id": modality_id,
        "athlete_id": athlete_id,
        "team_id": team_id,
    }

    matches = get_matches_table(
        match_id=match_id,
        tournament_id=tournament_id,
        modality_id=modality_id,
        athlete_id=athlete_id,
        team_id=team_id,
    )

    if match_id is not None and matches.count() == 0:
        # match was deleted
        rebuild_match_projection(match_id=match_id)
        logger.info(
            f"Updated projections for match_id={match_id} (match deleted).", extra=args
        )
        return

    c = 0
    for match in matches:
        rebuild_match_projection(match_id=match.id)
        c += 1

    logger.info(f"Updated projections for [{c}] matches.", extra=args)


@transaction.atomic
def update_nucleus_projections(nucleus_id: str = None) -> None:
    """Update the projections for the nucleus based on the provided parameters."""
    args = {"nucleus_id": nucleus_id}

    nucleus = get_nucleus_table(nucleus_id=nucleus_id)

    if nucleus_id is not None and nucleus.count() == 0:
        # nucleus was deleted
        rebuild_nucleo_projection(nucleo_id=nucleus_id)
        logger.info(
            f"Updated projections for nucleus_id={nucleus_id} (nucleus deleted).",
            extra=args,
        )
        return

    c = 0
    for n in nucleus:
        rebuild_nucleo_projection(nucleo_id=n.id)
        c += 1

    logger.info(f"Updated projections for [{c}] nucleus.", extra=args)


@transaction.atomic
def update_general_rankings_projections(season_id: str = None) -> None:
    """Update the projections for the general rankings based on the provided parameters."""
    args = {
        "season_id": season_id,
    }

    seasons = get_seasons_table(season_id=season_id)

    c = 0
    for season in seasons:
        rebuild_general_ranking_projection(season_id=season.id)
        c += 1

    logger.info(f"Updated projections for [{c}] seasons ranking.", extra=args)


@transaction.atomic
def update_modality_rankings_projections(
    season_id: str = None, modality_id: str = None
) -> None:
    """Update the projections for the modality rankings based on the provided parameters."""
    args = {
        "season_id": season_id,
        "modality_id": modality_id,
    }

    seasons = get_seasons_table(season_id=season_id)
    modalities = get_modalities_table(modality_id=modality_id)

    c = 0
    for season in seasons:
        for modality in modalities:
            rebuild_modality_ranking_projection(
                season_id=season.id, modality_id=modality.id
            )
            c += 1

    logger.info(
        f"Updated projections for [{c}] season-modality ranking combinations.",
        extra=args,
    )


@transaction.atomic
def update_seasons_projections(season_id: str = None) -> None:
    """Update the projections for the seasons based on the provided parameters."""
    args = {
        "season_id": season_id,
    }

    seasons = get_seasons_table(season_id=season_id)

    c = 0
    for season in seasons:
        rebuild_season_projection(season_id=season.id)
        c += 1

    logger.info(f"Updated projections for [{c}] seasons.", extra=args)


@transaction.atomic
def update_tournaments_projections(tournament_id: str = None) -> None:
    """Update the projections for the tournaments based on the provided parameters."""
    args = {
        "tournament_id": tournament_id,
    }

    tournaments = get_tournaments_table(tournament_id=tournament_id)

    if tournament_id is not None and tournaments.count() == 0:
        # tournament was deleted
        rebuild_tournament_projection(tournament_id=tournament_id)
        logger.info(
            f"Updated projections for tournament_id={tournament_id} (tournament deleted).",
            extra=args,
        )
        return

    c = 0
    for tournament in tournaments:
        rebuild_tournament_projection(tournament_id=tournament.id)
        c += 1

    logger.info(f"Updated projections for [{c}] tournaments.", extra=args)


@transaction.atomic
def update_tournament_standings_projections(
    tournament_id: str = None, team_id: str = None, athlete_id: str = None
) -> None:
    """Update the projections for the tournament standings based on the provided parameters."""
    args = {
        "tournament_id": tournament_id,
    }

    tournaments = get_tournaments_table(
        tournament_id=tournament_id, team_id=team_id, athlete_id=athlete_id
    )

    if tournament_id is not None and tournaments.count() == 0:
        # tournament was deleted
        rebuild_tournament_standings_projection(tournament_id=tournament_id)
        logger.info(
            f"Updated projections for tournament_id={tournament_id} (tournament deleted).",
            extra=args,
        )
        return

    c = 0
    for tournament in tournaments:
        rebuild_tournament_standings_projection(tournament_id=tournament.id)
        c += 1

    logger.info(f"Updated projections for [{c}] tournament standings.", extra=args)


@transaction.atomic
def update_regulations_projections(regulation_id: str = None) -> None:
    """Update the projections for the regulations based on the provided parameters."""
    args = {
        "regulation_id": regulation_id,
    }

    regulations = get_regulations_table(regulation_id=regulation_id)

    if regulation_id is not None and regulations.count() == 0:
        # regulation was deleted
        rebuild_regulation_projection(regulation_id=regulation_id)
        logger.info(
            f"Updated projections for regulation_id={regulation_id} (regulation deleted).",
            extra=args,
        )
        return

    c = 0
    for regulation in regulations:
        rebuild_regulation_projection(regulation_id=regulation.id)
        c += 1

    logger.info(f"Updated projections for [{c}] regulations.", extra=args)
