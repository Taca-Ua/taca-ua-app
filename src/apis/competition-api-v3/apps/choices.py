from django.db import models


class ModalityTypeModes(models.TextChoices):
    MODALITY = "modality", "Modality"
    POINTS = "points", "Points"


class TournamentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    FINISHED = "finished", "Finished"


class TournamentCompetitorType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    TEAM = "team", "Team"
