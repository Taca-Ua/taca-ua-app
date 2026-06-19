from django.core.management.base import BaseCommand


def rebuild_teams_projection():
    from apps.teams.selectors import get_teams_table

    from ...models import TeamDetailView
    from ...service import rebuild_team_projection

    TeamDetailView.objects.all().delete()

    for team in get_teams_table().all():
        rebuild_team_projection(team.id)
        print(f"Team [{team.id}] OK.")
    print("Rebuild of all team projections triggered successfully")


def rebuild_students_projection():
    from apps.athletes.selectors import get_athletes_table

    from ...models import StudentDetailView
    from ...service import rebuild_student_projection

    StudentDetailView.objects.all().delete()

    for student in get_athletes_table().all():
        rebuild_student_projection(student.id)
        print(f"Student [{student.id}] OK.")
    print("Rebuild of all student projections triggered successfully")


def rebuild_tournaments_projection():
    from apps.tournaments.selectors import get_tournaments_table

    from ...models import TournamentDetailView
    from ...service import rebuild_tournament_projection

    TournamentDetailView.objects.all().delete()

    for tournament in get_tournaments_table().all():
        rebuild_tournament_projection(tournament.id)
        print(f"Tournament [{tournament.id}] OK.")
    print("Rebuild of all tournament projections triggered successfully")


def rebuild_matches_projection():
    from apps.matches.selectors import get_matches_table

    from ...models import MatchDetailView
    from ...service import rebuild_match_projection

    MatchDetailView.objects.all().delete()

    for match in get_matches_table().all():
        rebuild_match_projection(match.id)
        print(f"Match [{match.id}] OK.")
    print("Rebuild of all match projections triggered successfully")


def rebuild_tournaments_standings_projection():
    from apps.tournaments.selectors import get_tournaments_table

    from ...models import TournamentStandingsView
    from ...service import rebuild_tournament_standings_projection

    TournamentStandingsView.objects.all().delete()

    for tournament in get_tournaments_table().all():
        rebuild_tournament_standings_projection(tournament.id)
        print(f"Tournament standings [{tournament.id}] OK.")
    print("Rebuild of all tournament standings projections triggered successfully")


def rebuild_general_ranking_projection():
    from apps.seasons.selectors import get_seasons_table

    from ...models import GeneralRankingView
    from ...service import rebuild_general_ranking_projection

    GeneralRankingView.objects.all().delete()

    for season in get_seasons_table().all():
        rebuild_general_ranking_projection(season.id)
        print(f"Season [{season.id}] OK.")
    print("Rebuild of all general ranking projections triggered successfully")


def rebuild_modalities_ranking_projection():
    from apps.seasons.selectors import get_seasons_table

    from ...models import ModalityRankingView
    from ...service import rebuild_modality_ranking_projection

    ModalityRankingView.objects.all().delete()

    for season in get_seasons_table().all():
        for s_modality in season.season_modalities.all():
            rebuild_modality_ranking_projection(season.id, s_modality.modality.id)
            print(
                f"Modality ranking [{s_modality.modality.id}] for season [{season.id}] OK."
            )
    print("Rebuild of all modalities ranking projections triggered successfully")


def rebuild_nuclei_projection():
    from apps.nucleus.selectors import get_nucleus_table

    from ...models import NucleoDetailView
    from ...service import rebuild_nucleo_projection

    NucleoDetailView.objects.all().delete()

    for nucleo in get_nucleus_table().all():
        rebuild_nucleo_projection(nucleo.id)
        print(f"Nucleus [{nucleo.id}] OK.")
    print("Rebuild of all nuclei projections triggered successfully")


def rebuild_seasons_projection():
    from apps.seasons.selectors import get_seasons_table

    from ...models import SeasonDetailView
    from ...service import rebuild_season_projection

    SeasonDetailView.objects.all().delete()

    for season in get_seasons_table().all():
        rebuild_season_projection(season.id)
        print(f"Season [{season.id}] OK.")
    print("Rebuild of all seasons projections triggered successfully")


def rebuild_regulations_projection():
    from apps.regulations.selectors import get_regulations_table

    from ...models import RegulationDetailView
    from ...service import rebuild_regulation_projection

    RegulationDetailView.objects.all().delete()

    for regulation in get_regulations_table().all():
        rebuild_regulation_projection(regulation.id)
        print(f"Regulation [{regulation.id}] OK.")
    print("Rebuild of all regulations projections triggered successfully")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        rebuild_teams_projection()
        rebuild_students_projection()
        rebuild_tournaments_projection()
        rebuild_matches_projection()
        rebuild_tournaments_standings_projection()
        rebuild_general_ranking_projection()
        rebuild_modalities_ranking_projection()
        rebuild_nuclei_projection()
        rebuild_seasons_projection()
        rebuild_regulations_projection()
        pass
