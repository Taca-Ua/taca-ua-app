import uuid
from typing import TYPE_CHECKING

from apps.athletes.models import Athlete
from apps.staff.models import Staff
from apps.tournaments.models import Tournament, TournamentCompetitor
from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class MatchStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    FINISHED = "finished", "Finished"
    CANCELED = "canceled", "Canceled"


class Match(models.Model):
    """Represents a match within a tournament."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    location = models.CharField(max_length=255, blank=True, null=True)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=MatchStatus.choices, default=MatchStatus.SCHEDULED
    )
    journey = models.CharField(max_length=255, blank=True, null=True)

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )

    if TYPE_CHECKING:
        participants: RelatedManager["MatchParticipant"]
        comments: RelatedManager["MatchComment"]


class MatchParticipant(models.Model):
    """Represents a competitor participating in a match."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="participants"
    )
    competitor = models.ForeignKey(
        TournamentCompetitor,
        on_delete=models.CASCADE,
        related_name="match_participations",
    )

    # outcome fields
    score = models.FloatField(
        blank=True, null=True
    )  # Can represent points, gols, etc. depending on the sport
    position = models.IntegerField(
        blank=True, null=True
    )  # 1 for first place, 2 for second, etc.
    winner = models.BooleanField(
        blank=True, null=True
    )  # Indicates if this participant is the winner of the match (useful for binary outcomes)

    if TYPE_CHECKING:
        lineup: RelatedManager["MatchParticipantAthleteLineup"]
        staff: RelatedManager["MatchParticipantStaffAssignment"]

    class Meta:
        unique_together = ("match", "competitor")

    @property
    def entity_id(self):
        """Returns the ID of the underlying athlete or team, depending on the competitor type."""
        if self.competitor.athlete:
            return self.competitor.athlete.id
        elif self.competitor.team:
            return self.competitor.team.id
        return None

    @property
    def name(self):
        """Returns the name of the underlying athlete or team, depending on the competitor type."""
        if self.competitor.athlete:
            return self.competitor.athlete.name
        elif self.competitor.team:
            return self.competitor.team.name
        return None

    @property
    def logo_url(self):
        """Returns the logo URL of the underlying athlete or team, depending on the competitor type."""
        if self.competitor.athlete:
            return self.competitor.athlete.course.nucleus.logo_url
        elif self.competitor.team:
            return self.competitor.team.course.nucleus.logo_url
        return None


class MatchParticipantAthleteLineup(models.Model):
    """Represents a lineup of competitors for a match participant (e.g., team members)."""

    match_participant = models.ForeignKey(
        MatchParticipant, on_delete=models.CASCADE, related_name="lineup"
    )
    athlete = models.ForeignKey(
        Athlete, on_delete=models.CASCADE, related_name="match_lineups"
    )

    jersey_number = models.CharField(
        max_length=10, blank=True, null=True
    )  # Optional field for team sports
    is_starter = models.BooleanField(
        default=False
    )  # Indicates if the athlete is a starter in the lineup

    @property
    def player_name(self):
        return self.athlete.name

    @property
    def player_id(self):
        return self.athlete.id

    @property
    def player_course(self):
        return self.athlete.course.name

    class Meta:
        unique_together = ("match_participant", "athlete")


class MatchParticipantStaffAssignment(models.Model):
    """Represents staff assigned to a match participant (e.g., coaches, medical staff)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    match_participant = models.ForeignKey(
        MatchParticipant, on_delete=models.CASCADE, related_name="staff"
    )
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="match_assignments"
    )

    @property
    def name(self):
        return self.staff.name

    class Meta:
        unique_together = ("match_participant", "staff")


class MatchComment(models.Model):
    """Represents a comment made on a match."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="comments")

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=255)
    author_id = models.CharField(max_length=255)
