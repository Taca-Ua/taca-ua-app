from uuid import UUID

from apps.athletes.selectors import get_athlete_by_id
from apps.courses.selectors import get_course_by_id
from apps.matches.selectors import get_match_by_id
from apps.modalities.selectors import get_modality_by_id
from apps.nucleus.selectors import get_nucleus_by_id
from apps.ranking.selectors import get_general_ranking, get_modality_ranking
from apps.regulations.selectors import get_regulation_by_id
from apps.seasons.selectors import get_season_by_id
from apps.teams.selectors import get_team_by_id
from apps.tournaments.formats import FormatRegistry
from apps.tournaments.models import TournamentStatus
from apps.tournaments.selectors import get_tournament_by_id, get_tournament_results
from django.db import transaction

from .models import (
    CourseDetailView,
    GeneralRankingView,
    HomePageConfigView,
    MatchDetailView,
    ModalityRankingView,
    NucleoDetailView,
    RegulationDetailView,
    SeasonDetailView,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
)


@transaction.atomic(savepoint=False)
def rebuild_team_projection(team_id: UUID):
    from apps.teams.models import Team

    # delete existing projection for the team before creating a new one
    TeamDetailView.objects.filter(team_id=team_id).delete()

    try:
        team = get_team_by_id(team_id)
    except Team.DoesNotExist:
        return None

    modality_type = team.modality.modality_type(team.season_id)
    if not modality_type:
        return None

    # create a new projection for the team
    projection = TeamDetailView.objects.create(
        team_id=team.id,
        team_name=team.name,
        team_season_id=team.season_id,
        course_id=team.course_id,
        course_name=team.course.name,
        course_abbreviation=team.course.abbreviation,
        nucleo_id=team.course.nucleus.id,
        nucleo_name=team.course.nucleus.name,
        nucleo_abbreviation=team.course.nucleus.abbreviation,
        nucleo_logo_url=team.course.nucleus.logo_url,
        modality_id=team.modality_id,
        modality_name=team.modality.name,
        modality_type_id=modality_type.id,
        modality_type_name=modality_type.name,
        player_count=team.athletes.count(),
        players=[
            {
                "student_id": str(player.id) if player.id else None,
                "student_number": player.student_number,
                "full_name": player.name,
                "is_member": player.is_member,
            }
            for player in team.athletes.all()
        ],
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_student_projection(student_id: UUID):
    from apps.athletes.models import Athlete

    # delete existing projection for the student before creating a new one
    StudentDetailView.objects.filter(student_id=student_id).delete()

    try:
        student = get_athlete_by_id(student_id)
    except Athlete.DoesNotExist:
        return None

    # create a new projection for the student
    projection = StudentDetailView.objects.create(
        student_id=student.id,
        student_number=student.student_number,
        full_name=student.name,
        is_member=student.is_member,
        course_id=student.course.id,
        course_name=student.course.name,
        course_abbreviation=student.course.abbreviation,
        nucleo_id=student.course.nucleus.id,
        nucleo_name=student.course.nucleus.name,
        nucleo_abbreviation=student.course.nucleus.abbreviation,
        team_count=student.teams.count(),
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_tournament_projection(tournament_id: UUID):
    from apps.tournaments.models import Tournament

    # delete existing projection for the tournament before creating a new one
    TournamentDetailView.objects.filter(tournament_id=tournament_id).delete()

    try:
        tournament = get_tournament_by_id(tournament_id)
    except Tournament.DoesNotExist:
        return None

    # create a new projection for the tournament
    projection = TournamentDetailView.objects.create(
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        tournament_season_id=tournament.season_id,
        start_date=tournament.start_date,
        status=tournament.status,
        modality_id=tournament.modality_id,
        modality_name=tournament.modality.name,
        modality_type_id=tournament.modality.modality_type(tournament.season_id).id,
        modality_type_name=tournament.modality.modality_type(tournament.season_id).name,
        competitor_count=tournament.competitors.count(),
        match_count=tournament.matches.count(),
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_match_projection(match_id: UUID):
    from apps.matches.models import Match

    # delete existing projection for the match before creating a new one
    MatchDetailView.objects.filter(match_id=match_id).delete()

    # get the match data
    try:
        match = get_match_by_id(match_id)
    except Match.DoesNotExist:
        return None

    if match.scheduled_time is None:
        # if the match does not have location or scheduled time, we cannot build the projection
        return None

    # create a new projection for the match
    projection = MatchDetailView.objects.create(
        match_id=match.id,
        location=match.location or "TBD",
        status=match.status,
        start_time=match.scheduled_time,
        tournament_id=match.tournament.id,
        tournament_name=match.tournament.name,
        modality_id=match.tournament.modality_id,
        modality_name=match.tournament.modality.name,
        participants=[
            {
                "participant_id": str(participant.id),
                "competitor_id": str(participant.competitor.id),
                "participant_type": participant.participant_type,
                "competitor_entity_id": str(participant.entity_id),
                "participant_name": participant.name,
            }
            for participant in match.participants.all()
        ],
        results=[
            {
                "participant_id": str(participant.id),
                "score": participant.score,
                "position": participant.position,
            }
            for participant in match.participants.all()
        ],
        participant_count=match.participants.count(),
        comment_count=match.comments.count(),
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_tournament_standings_projection(tournament_id: UUID):
    from apps.tournaments.models import Tournament

    # delete existing projection for the tournament standings before creating a new one
    TournamentStandingsView.objects.filter(tournament_id=tournament_id).delete()

    try:
        tournament = get_tournament_by_id(tournament_id)
    except Tournament.DoesNotExist:
        return None

    tournament_format = FormatRegistry.get_format(tournament)
    standings = tournament_format.get_details().get("standings", [])
    standings_map = {standing["competitor_id"]: standing for standing in standings}

    if tournament.status == TournamentStatus.FINISHED:
        # use the inserted final standings
        results = get_tournament_results(tournament_id)

        projection = TournamentStandingsView.objects.bulk_create(
            [
                TournamentStandingsView(
                    tournament_id=tournament.id,
                    competitor_id=result.competitor.id,
                    competitor_type=tournament.competitor_type,
                    competitor_entity_id=result.competitor.entity_id,
                    competitor_name=result.competitor.name,
                    position=result.position,
                    # append any relevant statistics from the standings details if available
                    statistics_metadata=standings_map.get(result.competitor.id, {}).get(
                        "format_meta", None
                    ),
                )
                for result in results
            ]
        )
    elif standings:
        # use the calculated standings from the format details
        projection = TournamentStandingsView.objects.bulk_create(
            [
                TournamentStandingsView(
                    tournament_id=tournament.id,
                    competitor_id=competitor.id,
                    competitor_type=tournament.competitor_type,
                    competitor_entity_id=competitor.entity_id,
                    competitor_name=competitor.name,
                    position=standings_map.get(competitor.id, {}).get("position", 0),
                    statistics_metadata=standings_map.get(competitor.id, {}).get(
                        "format_meta", None
                    ),
                )
                for competitor in tournament.competitors.all()
                if competitor.id in standings_map
            ]
        )
    else:
        # use just the competitors ordered by their position as a fallback
        projection = TournamentStandingsView.objects.bulk_create(
            [
                TournamentStandingsView(
                    tournament_id=tournament.id,
                    competitor_id=competitor.id,
                    competitor_type=tournament.competitor_type,
                    competitor_entity_id=competitor.entity_id,
                    competitor_name=competitor.name,
                    position=idx,
                )
                for idx, competitor in enumerate(tournament.competitors.all(), start=1)
            ]
        )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_general_ranking_projection(season_id: int):
    # delete existing projection for the general ranking before creating a new one
    GeneralRankingView.objects.filter(season_id=season_id).delete()

    # get the general ranking data
    general_ranking = get_general_ranking(season_id)

    # create a new projection for the general ranking
    entries = []
    for idx, entry in enumerate(general_ranking, start=1):
        entries.append(
            GeneralRankingView(
                season_id=season_id,
                course_id=entry.course.id,
                course_name=entry.course.name,
                course_abbreviation=entry.course.abbreviation,
                nucleo_id=entry.course.nucleus.id,
                nucleo_name=entry.course.nucleus.name,
                nucleo_abbreviation=entry.course.nucleus.abbreviation,
                points=entry.points,
                rank=idx,
                tournaments_participated=entry.tournaments_participated,
            )
        )

    projection = GeneralRankingView.objects.bulk_create(entries)

    return projection


@transaction.atomic(savepoint=False)
def rebuild_modality_ranking_projection(season_id: int, modality_id: UUID):
    from apps.modalities.models import Modality

    # delete existing projection for the modality ranking before creating a new one
    ModalityRankingView.objects.filter(
        season_id=season_id, modality_id=modality_id
    ).delete()

    # get the modality data
    try:
        modality = get_modality_by_id(modality_id)
    except Modality.DoesNotExist:
        return None

    if modality.modality_type(season_id) is None:
        # if the modality type is not defined for the given season, we cannot build the ranking projection
        return None

    # get the modality ranking data
    modality_ranking = get_modality_ranking(season_id, modality_id)

    # create a new projection for the modality ranking
    entries = []
    for idx, entry in enumerate(modality_ranking, start=1):
        entries.append(
            ModalityRankingView(
                season_id=season_id,
                modality_id=modality.id,
                modality_name=modality.name,
                course_id=entry.course.id,
                course_name=entry.course.name,
                course_abbreviation=entry.course.abbreviation,
                nucleo_id=entry.course.nucleus.id,
                nucleo_name=entry.course.nucleus.name,
                nucleo_abbreviation=entry.course.nucleus.abbreviation,
                points=entry.points,
                rank=idx,
            )
        )

    projection = ModalityRankingView.objects.bulk_create(entries)

    return projection


@transaction.atomic(savepoint=False)
def rebuild_nucleo_projection(nucleo_id: UUID):
    from apps.nucleus.models import Nucleus

    # delete existing projection for the nucleo before creating a new one
    NucleoDetailView.objects.filter(nucleo_id=nucleo_id).delete()

    try:
        nucleo = get_nucleus_by_id(nucleo_id)
    except Nucleus.DoesNotExist:
        return None

    # create a new projection for the nucleo
    projection = NucleoDetailView.objects.create(
        nucleo_id=nucleo.id,
        name=nucleo.name,
        abbreviation=nucleo.abbreviation,
        logo_url=nucleo.logo_url,
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_season_projection(season_id: int):
    from apps.seasons.models import Season

    # delete existing projection for the season before creating a new one
    SeasonDetailView.objects.filter(season_id=season_id).delete()

    try:
        season = get_season_by_id(season_id)
    except Season.DoesNotExist:
        return None

    # create a new projection for the season
    projection = SeasonDetailView.objects.create(
        season_id=season.id,
        name=season.name,
        is_active=season.is_current,
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_regulation_projection(regulation_id: UUID):
    from apps.regulations.models import Regulation

    # delete existing projection for the regulation before creating a new one
    RegulationDetailView.objects.filter(id=regulation_id).delete()

    try:
        regulation = get_regulation_by_id(regulation_id)
    except Regulation.DoesNotExist:
        return None

    # create a new projection for the regulation
    projection = RegulationDetailView.objects.create(
        id=regulation.id,
        title=regulation.title,
        description=regulation.description,
        file_url=regulation.file_url,
        season_id=regulation.season_id,
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_home_page_config_projection():
    from apps.plataform_configs.models import PublicWebsiteHomePage, Sponsor

    # delete existing projection for the home page config before creating a new one
    HomePageConfigView.objects.all().delete()

    try:
        home_page_config = PublicWebsiteHomePage.objects.get()
    except PublicWebsiteHomePage.DoesNotExist:
        return None

    sponsors = Sponsor.objects.all()

    # create a new projection for the home page config
    projection = HomePageConfigView.objects.create(
        title=home_page_config.title,
        subtitle=home_page_config.subtitle,
        welcome_message=home_page_config.welcome_message,
        about_us=home_page_config.about_us,
        hero_image_url=home_page_config.hero_image_url,
        sponsors=[
            {
                "name": sponsor.name,
                "logo_url": sponsor.logo_url,
                "website_url": sponsor.website_url,
            }
            for sponsor in sponsors
        ],
    )

    return projection


@transaction.atomic(savepoint=False)
def rebuild_course_projection(course_id: UUID):
    from apps.courses.models import Course

    # delete existing projection for the course before creating a new one
    CourseDetailView.objects.filter(course_id=course_id).delete()

    try:
        course = get_course_by_id(course_id)
    except Course.DoesNotExist:
        return None

    # create a new projection for the course
    projection = CourseDetailView.objects.create(
        course_id=course.id,
        name=course.name,
        abbreviation=course.abbreviation,
        nucleo_id=course.nucleus.id,
        nucleo_name=course.nucleus.name,
        nucleo_abbreviation=course.nucleus.abbreviation,
        nucleo_logo_url=course.nucleus.logo_url,
    )

    return projection
