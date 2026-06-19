from django.db import models


class TeamDetailView(models.Model):
    """Materialized view: Team with course, nucleo, and modality details."""

    team_id = models.UUIDField(primary_key=True)
    team_name = models.CharField(max_length=255)
    team_season_id = models.IntegerField()

    course_id = models.UUIDField()
    course_name = models.CharField(max_length=255)
    course_abbreviation = models.CharField(max_length=255)

    nucleo_id = models.UUIDField()
    nucleo_name = models.CharField(max_length=255)
    nucleo_abbreviation = models.CharField(max_length=255)
    nucleo_logo_url = models.CharField(max_length=255)

    modality_id = models.UUIDField()
    modality_name = models.CharField(max_length=255)
    modality_type_id = models.UUIDField()
    modality_type_name = models.CharField(max_length=255)

    player_count = models.IntegerField()
    players = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["course_id"]),
            models.Index(fields=["nucleo_id"]),
            models.Index(fields=["modality_id"]),
        ]


class StudentDetailView(models.Model):
    """Materialized view: Student with course and nucleo details."""

    student_id = models.UUIDField(primary_key=True)
    student_number = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    is_member = models.BooleanField()

    course_id = models.UUIDField()
    course_name = models.CharField(max_length=255)
    course_abbreviation = models.CharField(max_length=255)

    nucleo_id = models.UUIDField()
    nucleo_name = models.CharField(max_length=255)
    nucleo_abbreviation = models.CharField(max_length=255)

    team_count = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["course_id"]),
            models.Index(fields=["nucleo_id"]),
            models.Index(fields=["student_number"]),
        ]


class TournamentDetailView(models.Model):
    """Materialized view: Tournament with modality and competitor details."""

    tournament_id = models.UUIDField(primary_key=True)
    tournament_name = models.CharField(max_length=255)
    tournament_season_id = models.IntegerField()
    start_date = models.DateField()
    status = models.CharField(max_length=255)

    modality_id = models.UUIDField()
    modality_name = models.CharField(max_length=255)
    modality_type_id = models.UUIDField()
    modality_type_name = models.CharField(max_length=255)

    competitor_count = models.IntegerField()
    match_count = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["modality_id"]),
        ]


class MatchDetailView(models.Model):
    """Materialized view: Match with tournament, participants, and result details."""

    match_id = models.UUIDField(primary_key=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    start_time = models.DateTimeField()

    tournament_id = models.UUIDField()
    tournament_name = models.CharField(max_length=255)

    modality_id = models.UUIDField()
    modality_name = models.CharField(max_length=255)

    participants = models.JSONField()  # List of participants with details
    results = models.JSONField()  # Match results details

    participant_count = models.IntegerField()
    comment_count = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_time"]),
            models.Index(fields=["tournament_id"]),
            models.Index(fields=["modality_id"]),
        ]


class TournamentStandingsView(models.Model):
    """Materialized view: Tournament standings/rankings."""

    pk = models.CompositePrimaryKey("tournament_id", "competitor_id")

    tournament_id = models.UUIDField()
    competitor_id = models.UUIDField()
    competitor_type = models.CharField(max_length=255)
    competitor_entity_id = models.UUIDField()
    competitor_name = models.CharField(max_length=255)
    position = models.IntegerField()

    statistics_metadata = models.JSONField(
        null=True, default=None
    )  # JSON field to store various statistics

    class Meta:
        indexes = [
            models.Index(fields=["tournament_id"]),
        ]


class GeneralRankingView(models.Model):
    """Materialized view: General ranking across all courses."""

    season_id = models.IntegerField()
    course_id = models.UUIDField()
    course_name = models.CharField(max_length=255)
    course_abbreviation = models.CharField(max_length=255)

    nucleo_id = models.UUIDField()
    nucleo_name = models.CharField(max_length=255)
    nucleo_abbreviation = models.CharField(max_length=255)

    points = models.IntegerField()
    rank = models.IntegerField()

    tournaments_participated = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["season_id"]),
            models.Index(fields=["rank"]),
            models.Index(fields=["course_id"]),
        ]


class ModalityRankingView(models.Model):
    """Materialized view: Modality-specific ranking for courses."""

    season_id = models.IntegerField()
    modality_id = models.UUIDField()
    modality_name = models.CharField(max_length=255)

    course_id = models.UUIDField()
    course_name = models.CharField(max_length=255)
    course_abbreviation = models.CharField(max_length=255)

    nucleo_id = models.UUIDField()
    nucleo_name = models.CharField(max_length=255)
    nucleo_abbreviation = models.CharField(max_length=255)

    points = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["season_id"]),
            models.Index(fields=["modality_id"]),
            models.Index(fields=["rank"]),
        ]


class NucleoDetailView(models.Model):
    """Materialized view: Nucleo details with aggregated statistics."""

    nucleo_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255)
    logo_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["nucleo_id"]),
        ]


class SeasonDetailView(models.Model):
    """Materialized view: Season details with aggregated statistics."""

    season_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField()

    class Meta:
        indexes = [
            models.Index(fields=["season_id"]),
        ]


class RegulationDetailView(models.Model):
    """Materialized view: Regulation details with aggregated statistics."""

    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file_url = models.CharField(max_length=255)
    season_id = models.IntegerField()
