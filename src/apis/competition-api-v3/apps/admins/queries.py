from django.db.models import QuerySet

from .models import Admin


def list_admins() -> QuerySet[Admin]:
    queryset = Admin.objects.all()
    return queryset


def get_admin_by_id(user_id: str) -> QuerySet[Admin]:
    queryset = Admin.objects.filter(id=user_id)
    if not queryset.exists():
        raise Admin.DoesNotExist(f"Admin with ID {user_id} does not exist")

    return queryset
