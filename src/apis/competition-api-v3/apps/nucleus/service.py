from django.db import transaction
from rest_framework.exceptions import ValidationError
from shared.file_storage.minio_service import MinioService

from .models import Nucleus

# init the MinioService for handling file storage related to nucleus logos
file_storage_service = MinioService("nucleus-logos")


@transaction.atomic
def create_nucleo(name: str, abbreviation: str, image: bytes = None) -> Nucleus:
    """Creates a new nucleo and uploads its logo if an image is provided."""
    image_url = file_storage_service.upload_file(image) if image else None

    nucleo = Nucleus.objects.create(
        name=name, abbreviation=abbreviation, logo_url=image_url
    )

    return nucleo


@transaction.atomic
def update_nucleo(
    nucleo_id: str, name: str = None, abbreviation: str = None, image: bytes = None
) -> Nucleus:
    """Updates a nucleo's details and its associated logo if a new image is provided."""

    nucleo = Nucleus.objects.get(id=nucleo_id)
    if nucleo is None:
        raise ValidationError("Nucleo not found")

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

    nucleo.save()

    return nucleo


@transaction.atomic
def delete_nucleo(nucleo_id: str) -> None:
    """Deletes a nucleo and its associated logo from storage if it exists."""

    nucleo = Nucleus.objects.get(id=nucleo_id)
    if nucleo is None:
        raise ValidationError("Nucleo not found")

    logo_url = nucleo.logo_url
    nucleo.delete()

    if logo_url:
        file_storage_service.delete_file(logo_url)
