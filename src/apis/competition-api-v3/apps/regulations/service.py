from apps.seasons.selectors import get_current_season
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from shared.file_storage.minio_service import MinioService

from .models import Regulation

# init the MinioService for handling file storage related to regulations
file_storage_service = MinioService("regulations")


@transaction.atomic
def create_regulation(
    file: UploadedFile, title: str, description: str = None, season_id: int = None
) -> Regulation:
    """
    Create a new regulation.

    Args:
        file (UploadedFile): The uploaded regulation file.
        title (str): The title of the regulation.
        description (str, optional): The description of the regulation. Defaults to None.
        season_id (int, optional): The ID of the season to which the regulation belongs. Defaults to None.
    """

    if season_id is None:
        season_id = get_current_season().id

    # Upload the file to Minio and get the file URL
    file_url = file_storage_service.upload_file(file)

    regulation = Regulation.objects.create(
        file_url=file_url, title=title, description=description, season_id=season_id
    )
    return regulation


@transaction.atomic
def update_regulation(
    regulation_id: str,
    file: UploadedFile = None,
    title: str = None,
    description: str = None,
) -> Regulation:
    """
    Update an existing regulation.

    Args:
        regulation_id (str): The UUID of the regulation to update.
        file (UploadedFile, optional): The new uploaded regulation file. Defaults to None.
        title (str, optional): The new title of the regulation. Defaults to None.
        description (str, optional): The new description of the regulation. Defaults to None.

    Returns:
        Regulation: The updated Regulation instance.

    Raises:
        Regulation.DoesNotExist: If the regulation with the specified ID does not exist.
    """
    regulation = get_regulation(regulation_id)

    if file is not None:
        regulation.file_url = file_storage_service.update_file(
            regulation.file_url, file
        )
    if title is not None:
        regulation.title = title
    if description is not None:
        regulation.description = description

    regulation.save()
    return regulation


@transaction.atomic
def delete_regulation(regulation_id: str) -> None:
    """
    Delete a regulation by its ID.

    Args:
        regulation_id (str): The UUID of the regulation to delete.

    Raises:
        Regulation.DoesNotExist: If the regulation with the specified ID does not exist.
    """
    regulation = get_regulation(regulation_id)

    file_storage_service.delete_file(regulation.file_url)
    regulation.delete()


def get_regulation(regulation_id: str) -> Regulation:
    """
    Retrieve a regulation by its ID.

    Args:
        regulation_id (str): The UUID of the regulation to retrieve.

    Returns:
        Regulation: The requested Regulation instance.

    Raises:
        Regulation.DoesNotExist: If the regulation with the specified ID does not exist.
    """
    try:
        return Regulation.objects.get(id=regulation_id)
    except Regulation.DoesNotExist:
        raise Regulation.DoesNotExist(
            f"Regulation with id {regulation_id} does not exist."
        )
