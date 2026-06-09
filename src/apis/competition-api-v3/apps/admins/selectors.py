from django.db.models import QuerySet

from .models import Admin


def get_admin_table(include_inactive: bool = False) -> QuerySet[Admin]:
    """Get a queryset of all admins with related nucleus information"""

    queryset = Admin.objects.prefetch_related("nucleos__courses").all()

    if not include_inactive:
        queryset = queryset.filter(active=True)

    return queryset


def get_admin_by_id(admin_id: str) -> Admin:
    """Get a single admin by ID with related nucleus information"""

    return get_admin_table(include_inactive=True).get(id=admin_id)
