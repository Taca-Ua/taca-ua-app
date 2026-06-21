import logging

from apps.modality_types.models import ModalityType
from apps.tournaments.models import Tournament, TournamentStatus
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from workers.ranking_updater.service import request_ranking_recomputation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ModalityType)
def on_modality_type_save(sender, instance: ModalityType, created, **kwargs):
    """Signal to handle changes when a ModalityType is updated."""
    if created:
        return

    # recalc rankings
    request_ranking_recomputation(modality_type_id=instance.id)


@receiver(pre_save, sender=Tournament)
def on_tournament_competitors_changed(sender, instance: Tournament, **kwargs):
    if instance.pk is None:
        # New instance, skip
        return

    if instance.status != TournamentStatus.FINISHED:
        # no need to recalc rankings if tournament is not finished
        return

    old_instance = Tournament.objects.get(pk=instance.pk)

    if old_instance.status != TournamentStatus.FINISHED:
        # tournament is being marked as finished,
        # rankings will be updated in ther service
        return

    # check if the competitors have changed
    if not (
        old_instance.competitors.count()
        == instance.competitors.count()  # check if the number of competitors has changed
        and set(old_instance.competitors.values_list("id", flat=True))
        == set(
            instance.competitors.values_list("id", flat=True)
        )  # check if the competitors have changed
    ):
        return

    if old_instance.rank == instance.rank:
        # if the rank has not changed, no need to recalc rankings
        return

    # recalc rankings
    request_ranking_recomputation(tournament_id=instance.id)
