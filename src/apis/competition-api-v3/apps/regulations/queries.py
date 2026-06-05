from django.db.models import QuerySet
from uuid import UUID
from .models import Regulation

def get_all_regulations() -> QuerySet[Regulation]:
    """
    Retrieve all regulations from the database.

    Returns:
        QuerySet[Regulation]: A queryset containing all Regulation instances.
    """
    return Regulation.objects.all()

def get_regulation_by_id(regulation_id: UUID) -> QuerySet[Regulation]:
    """
    Retrieve a regulation by its ID.

    Args:
        regulation_id (str): The UUID of the regulation to retrieve.

    Returns:
        Regulation: The Regulation instance with the specified ID, or None if not found.
    """
    queryset = Regulation.objects.filter(id=regulation_id)
    if not queryset.exists():
        raise Regulation.DoesNotExist(f"Regulation with id {regulation_id} does not exist.")

    return queryset.first()