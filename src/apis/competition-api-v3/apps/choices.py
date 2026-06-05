from django.db import models


class ModalityTypeModes(models.TextChoices):
    MODALITY = "modality", "Modality"
    POINTS = "points", "Points"


class TournamentStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    FINISHED = "FINISHED", "Finished"


class TournamentCompetitorType(models.TextChoices):
    INDIVIDUAL = "INDIVIDUAL", "Individual"
    TEAM = "TEAM", "Team"
