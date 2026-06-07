from django.db.models import QuerySet

from ..models import Admin


def render_admin_list(admins: QuerySet[Admin] | Admin) -> QuerySet[Admin]:
    if isinstance(admins, Admin):
        admins = Admin.objects.filter(id=admins.id)
    return admins


def render_admin_detail(admin: QuerySet[Admin] | Admin) -> QuerySet[Admin]:

    if isinstance(admin, Admin):
        admin = Admin.objects.filter(id=admin.id)

    admin = render_admin_list(admin)

    admin = admin.prefetch_related("nucleos", "nucleos__courses")

    return admin
