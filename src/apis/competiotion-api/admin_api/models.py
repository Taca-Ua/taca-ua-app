"""
Django models for Admin API - Aggregated from microservices.
This is a monolithic implementation combining models from:
- matches-service
- modalities-service
- ranking-service
- tournaments-service
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# ==================== MATCHES MODELS ====================


class MatchStatus(models.TextChoices):
    """Enum for match status"""

    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    FINISHED = "finished", "Finished"
    CANCELLED = "cancelled", "Cancelled"


class Match(models.Model):
    """
    Represents a match/game in a tournament.
    Originally from: matches-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament_id = models.UUIDField(db_index=True)
    team_home_id = models.UUIDField(db_index=True)
    team_away_id = models.UUIDField(db_index=True)
    location = models.TextField()
    start_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=MatchStatus.choices, default=MatchStatus.SCHEDULED
    )
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    additional_details = models.JSONField(null=True, blank=True)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "match"
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"Match {self.id} - {self.status}"


class Lineup(models.Model):
    """
    Stores lineup/roster information for a match.
    Originally from: matches-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    team_id = models.UUIDField(db_index=True)
    player_id = models.UUIDField()
    jersey_number = models.IntegerField()
    is_starter = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "lineup"
        verbose_name = "Lineup"
        verbose_name_plural = "Lineups"

    def __str__(self):
        return f"Lineup {self.id} - Match {self.match_id}, Player {self.player_id}"


class Comment(models.Model):
    """
    Stores comments for a match.
    Originally from: matches-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, db_index=True)
    message = models.TextField()
    author_id = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "comment"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment {self.id} - Match {self.match_id}"


# ==================== MODALITIES MODELS ====================


# used
class Nucleo(models.Model):
    """
    Represents an academic nucleos.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    abbreviation = models.TextField(unique=True)

    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "nucleo"
        verbose_name = "Nucleo"
        verbose_name_plural = "Nucleos"

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Represents an academic course.
    Originally from: modalities-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    abbreviation = models.TextField(unique=True)
    nucleo = models.ForeignKey(Nucleo, on_delete=models.DO_NOTHING, db_index=True)

    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.abbreviation}: {self.name}"


# used
class ModalityType(models.Model):
    """
    Enumeration for modality types.
    Originally from: modalities-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True)
    description = models.TextField(null=True, blank=True)
    escaloes = models.JSONField(null=True, blank=True)  # Array of text stored as JSON
    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "modality_type"
        verbose_name = "Modality Type"
        verbose_name_plural = "Modality Types"

    def __str__(self):
        return self.name


# used
class Modality(models.Model):
    """
    Represents a sport modality.
    Originally from: modalities-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True)
    modality_type = models.ForeignKey(
        ModalityType, on_delete=models.DO_NOTHING, db_index=True
    )

    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "modality"
        verbose_name = "Modality"
        verbose_name_plural = "Modalities"

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Represents a team for a modality and course.
    Originally from: modalities-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modality_id = models.UUIDField(db_index=True)
    course_id = models.UUIDField(db_index=True)
    name = models.TextField()
    players = models.JSONField(null=True, blank=True)  # Array of UUIDs stored as JSON
    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "team"
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Represents a member.
    Originally from: modalities-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField()
    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = "member"
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def __str__(self):
        return self.full_name


class Student(Member):
    """
    Represents a student.
    Originally from: modalities-service
    """

    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, db_index=True)
    student_number = models.TextField(unique=True)
    is_member = models.BooleanField(default=False)

    class Meta:
        db_table = "student"
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.full_name} ({self.student_number})"


class Staff(Member):
    """
    Represents a staff member.
    Originally from: modalities-service
    """

    staff_number = models.TextField(unique=True, null=True, blank=True)
    contact = models.TextField(unique=True, null=True, blank=True)

    def clean(self):

        # treat empty/whitespace-only strings as not set
        staff_ok = bool(self.staff_number and str(self.staff_number).strip())
        contact_ok = bool(self.contact and str(self.contact).strip())

        if not (staff_ok or contact_ok):
            raise ValidationError(
                "At least one of 'staff_number' or 'contact' must be set."
            )

    def save(self, *args, **kwargs):
        # normalize empty strings to None
        if isinstance(self.staff_number, str) and not self.staff_number.strip():
            self.staff_number = None
        if isinstance(self.contact, str) and not self.contact.strip():
            self.contact = None

        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "staff"
        verbose_name = "Staff"
        verbose_name_plural = "Staff Members"

    def __str__(self):
        return f"{self.full_name} ({self.staff_number})"


# ==================== RANKING MODELS ====================


class ModalityRanking(models.Model):
    """
    Represents rankings for a modality (sport) in a season.
    Aggregates team/course performance across all tournaments of this modality.
    Originally from: ranking-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modality_id = models.UUIDField(db_index=True)
    season_id = models.UUIDField(db_index=True)
    course_id = models.UUIDField(db_index=True)
    points = models.FloatField(default=0.0)
    details = models.JSONField(null=True, blank=True)  # Additional ranking details
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "modality_ranking"
        verbose_name = "Modality Ranking"
        verbose_name_plural = "Modality Rankings"

    def __str__(self):
        return (
            f"Course {self.course_id} in Modality {self.modality_id}: {self.points} pts"
        )


class CourseRanking(models.Model):
    """
    Represents overall rankings for a course in a season.
    Aggregates points from all modalities.
    Originally from: ranking-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField(db_index=True)
    season_id = models.UUIDField(db_index=True)
    total_points = models.FloatField(default=0.0)
    modality_breakdown = models.JSONField(null=True, blank=True)  # Points per modality
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_ranking"
        verbose_name = "Course Ranking"
        verbose_name_plural = "Course Rankings"

    def __str__(self):
        return f"Course {self.course_id}: {self.total_points} pts"


class GeneralRanking(models.Model):
    """
    Represents the general/overall ranking across all courses.
    This is a denormalized view for quick access.
    Originally from: ranking-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season_id = models.UUIDField(db_index=True)
    course_id = models.UUIDField(db_index=True)
    position = models.IntegerField()
    total_points = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "general_ranking"
        verbose_name = "General Ranking"
        verbose_name_plural = "General Rankings"

    def __str__(self):
        return f"Position {self.position}: Course {self.course_id} ({self.total_points} pts)"


# ==================== TOURNAMENTS MODELS ====================


class TournamentStatus(models.TextChoices):
    """Enum for tournament status"""

    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    FINISHED = "finished", "Finished"


class Tournament(models.Model):
    """
    Represents a tournament.
    Originally from: tournaments-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modality_id = models.UUIDField(db_index=True)
    name = models.TextField()
    season_id = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=20, choices=TournamentStatus.choices, default=TournamentStatus.DRAFT
    )
    rules = models.JSONField(null=True, blank=True)
    teams = models.JSONField(null=True, blank=True)  # Array of UUIDs stored as JSON
    start_date = models.DateTimeField(null=True, blank=True)
    created_by = models.UUIDField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    finished_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "tournament"
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"

    def __str__(self):
        return f"{self.name} ({self.status})"


class Stage(models.Model):
    """
    Represents a stage within a tournament (e.g., group stage, playoffs).
    Originally from: tournaments-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, db_index=True)
    name = models.TextField()
    order = models.IntegerField()

    class Meta:
        db_table = "stage"
        verbose_name = "Stage"
        verbose_name_plural = "Stages"

    def __str__(self):
        return f"{self.name} (Order: {self.order})"


class Journey(models.Model):
    """
    Represents a journey/round within a stage (e.g., matchday, round).
    Originally from: tournaments-service
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, db_index=True)
    number = models.IntegerField()

    class Meta:
        db_table = "journey"
        verbose_name = "Journey"
        verbose_name_plural = "Journeys"

    def __str__(self):
        return f"Journey {self.number}"
