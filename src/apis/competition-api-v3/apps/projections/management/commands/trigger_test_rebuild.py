from django.core.management.base import BaseCommand


def rebuild_random_team_projection():
    from apps.teams.selectors import get_teams_table

    from ...service import rebuild_team_projection

    random_team = get_teams_table().first()
    if not random_team:
        print("No teams found to trigger rebuild of team projection")
        return

    random_team_id = random_team.id
    print(f"Triggering rebuild of team projection for team_id: {random_team_id}")
    rebuild_team_projection(random_team_id)
    print("Rebuild of team projection triggered successfully")


def rebuild_random_student_projection():
    from apps.athletes.selectors import get_athletes_table

    from ...service import rebuild_student_projection

    random_student = get_athletes_table().first()
    if not random_student:
        print("No students found to trigger rebuild of student projection")
        return

    random_student_id = random_student.id
    print(
        f"Triggering rebuild of student projection for student_id: {random_student_id}"
    )
    rebuild_student_projection(random_student_id)
    print("Rebuild of student projection triggered successfully")


def rebuild_random_tournament_projection():
    from apps.tournaments.selectors import get_tournaments_table

    from ...service import rebuild_tournament_projection

    random_tournament = get_tournaments_table().first()
    if not random_tournament:
        print("No tournaments found to trigger rebuild of tournament projection")
        return

    random_tournament_id = random_tournament.id
    print(
        f"Triggering rebuild of tournament projection for tournament_id: {random_tournament_id}"
    )
    rebuild_tournament_projection(random_tournament_id)
    print("Rebuild of tournament projection triggered successfully")


def rebuild_random_match_projection():
    from apps.matches.selectors import get_matches_table

    from ...service import rebuild_match_projection

    random_match = get_matches_table().first()
    if not random_match:
        print("No matches found to trigger rebuild of match projection")
        return

    random_match_id = random_match.id
    print(f"Triggering rebuild of match projection for match_id: {random_match_id}")
    rebuild_match_projection(random_match_id)
    print("Rebuild of match projection triggered successfully")


def rebuild_random_tournament_standings_projection():
    from apps.tournaments.selectors import get_tournaments_table

    from ...service import rebuild_tournament_standings_projection

    random_tournament = get_tournaments_table().first()
    if not random_tournament:
        print(
            "No tournaments found to trigger rebuild of tournament standings projection"
        )
        return

    random_tournament_id = random_tournament.id
    print(
        f"Triggering rebuild of tournament standings projection for tournament_id: {random_tournament_id}"
    )
    rebuild_tournament_standings_projection(random_tournament_id)
    print("Rebuild of tournament standings projection triggered successfully")


def rebuild_general_ranking_projection():
    from apps.seasons.selectors import get_current_season

    from ...service import rebuild_general_ranking_projection

    current_season = get_current_season()

    print("Triggering rebuild of general ranking projection")
    rebuild_general_ranking_projection(current_season.id)
    print("Rebuild of general ranking projection triggered successfully")


def rebuild_random_modality_ranking_projection():
    from apps.modalities.selectors import get_modalities_table
    from apps.seasons.selectors import get_current_season

    from ...service import rebuild_modality_ranking_projection

    random_season = get_current_season()

    random_modality = get_modalities_table().first()
    if not random_modality:
        print("No modalities found to trigger rebuild of modality ranking projection")
        return

    random_season_id = random_season.id
    random_modality_id = random_modality.id
    print(
        f"Triggering rebuild of modality ranking projection for season_id: {random_season_id}, modality_id: {random_modality_id}"
    )
    rebuild_modality_ranking_projection(random_season_id, random_modality_id)
    print("Rebuild of modality ranking projection triggered successfully")


def rebuild_random_nucleus_projection():
    from apps.nucleus.selectors import get_nucleus_table

    from ...service import rebuild_nucleo_projection

    random_nucleus = get_nucleus_table().first()
    if not random_nucleus:
        print("No nucleus found to trigger rebuild of nucleus projection")
        return

    random_nucleus_id = random_nucleus.id
    print(
        f"Triggering rebuild of nucleus projection for nucleus_id: {random_nucleus_id}"
    )
    rebuild_nucleo_projection(random_nucleus_id)
    print("Rebuild of nucleus projection triggered successfully")


def rebuild_random_season_projection():
    from apps.seasons.selectors import get_seasons_table

    from ...service import rebuild_season_projection

    random_season = get_seasons_table().first()
    if not random_season:
        print("No seasons found to trigger rebuild of season projection")
        return

    random_season_id = random_season.id
    print(f"Triggering rebuild of season projection for season_id: {random_season_id}")
    rebuild_season_projection(random_season_id)
    print("Rebuild of season projection triggered successfully")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        rebuild_random_team_projection()
        rebuild_random_student_projection()
        rebuild_random_tournament_projection()
        rebuild_random_match_projection()
        rebuild_random_tournament_standings_projection()
        rebuild_general_ranking_projection()
        rebuild_random_modality_ranking_projection()
        rebuild_random_nucleus_projection()
        rebuild_random_season_projection()
