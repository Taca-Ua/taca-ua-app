from apps.seasons.selectors import get_current_season, get_season_by_id
from django.db import transaction
from rest_framework.exceptions import ValidationError
from shared.file_storage.minio_service import MinioService

from .models import Nucleus
from .selectors import get_nucleus_by_id

# init the MinioService for handling file storage related to nucleus logos
file_storage_service = MinioService("nucleus-logos")


@transaction.atomic
def create_nucleo(name: str, abbreviation: str, image: bytes = None) -> Nucleus:
    """Creates a new nucleo and uploads its logo if an image is provided."""
    image_url = file_storage_service.upload_file(image) if image else None

    nucleo = Nucleus.objects.create(
        name=name, abbreviation=abbreviation, logo_url=image_url
    )

    # add the newly created nucleo to the current season
    season = get_current_season()
    nucleo.seasons.add(season)

    return nucleo


@transaction.atomic
def update_nucleo(
    nucleo_id: str,
    name: str = None,
    abbreviation: str = None,
    image: bytes = None,
    entity_type: str = None,
) -> Nucleus:
    """Updates a nucleo's details and its associated logo if a new image is provided."""

    nucleo = get_nucleus_by_id(nucleo_id)

    if name:
        nucleo.name = name

    if abbreviation:
        nucleo.abbreviation = abbreviation

    if image:
        if nucleo.logo_url:
            # there is already an image, so we update it instead of uploading a new one
            file_storage_service.update_file(nucleo.logo_url, image)
        else:
            # there is no existing image, so we upload a new one
            image_url = file_storage_service.upload_file(image)
            nucleo.logo_url = image_url

    if entity_type:
        if entity_type not in Nucleus.NucleusEntityType.values:
            raise ValidationError(f"Invalid entity type: {entity_type}")
        nucleo.entity_type = entity_type

    nucleo.save()

    return nucleo


@transaction.atomic
def delete_nucleo(nucleo_id: str) -> None:
    """Deletes a nucleo and its associated logo from storage if it exists."""

    nucleo = get_nucleus_by_id(nucleo_id)

    logo_url = nucleo.logo_url
    nucleo.delete()

    if logo_url:
        file_storage_service.delete_file(logo_url)


@transaction.atomic
def add_nucleus_to_season(nucleus_id: str, season_id: str) -> Nucleus:
    """Adds a nucleus to a season."""
    nucleus = get_nucleus_by_id(nucleus_id)

    season = get_season_by_id(season_id)

    nucleus.seasons.add(season)

    return nucleus


@transaction.atomic
def remove_nucleus_from_season(nucleus_id: str, season_id: str) -> Nucleus:
    """Removes a nucleus from a season."""
    nucleus = get_nucleus_by_id(nucleus_id)
    season = get_season_by_id(season_id)

    if not nucleus.seasons.filter(id=season.id).exists():
        raise ValidationError(f"Nucleus is not associated with season {season_id}")

    if nucleus.courses.filter(seasons__id=season.id).exists():
        raise ValidationError(
            f"Nucleus has courses associated with season {season_id}. Cannot remove."
        )

    nucleus.seasons.remove(season)

    return nucleus
