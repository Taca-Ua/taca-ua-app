from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, QuerySet, Subquery
from django.db.models.functions import JSONObject

from .models import Modality, SeasonModality


def get_modalities_table(
    season_id: int = None, modality_id: int = None
) -> QuerySet[Modality]:
    queryset = Modality.objects.all()

    if modality_id:
        queryset = queryset.filter(id=modality_id)

    if season_id:
        season_modality_qs = SeasonModality.objects.filter(
            modality=OuterRef("pk"), season_id=season_id, modality_type__isnull=False
        )

        queryset = queryset.annotate(
            belongs_to_season=Exists(
                SeasonModality.objects.filter(
                    modality=OuterRef("pk"), season_id=season_id
                )
            ),
            # cannot anotate the whole modality type object, so we annotate a JSON object with the relevant fields
            modality_type=Subquery(
                season_modality_qs.annotate(
                    modality_type_json=JSONObject(
                        id="modality_type__id",
                        name="modality_type__name",
                    )
                ).values("modality_type_json")[:1]
            ),
        )
    return queryset


def get_modality_by_id(modality_id: int, *, season_id: int = None) -> Modality:
    modality_qs = get_modalities_table(season_id=season_id).filter(id=modality_id)

    if season_id:
        modality_qs = modality_qs.annotate(
            relevant_seasons_ids=ArrayAgg("modality_seasons__season_id", distinct=True)
        )

    return modality_qs.get()
