from admin_api.modules.admins import urlpatterns as admin_urls
from admin_api.modules.athletes import urlpatterns as athletes_urls
from admin_api.modules.courses import urlpatterns as courses_urls
from admin_api.modules.matches import urlpatterns as matches_urls
from admin_api.modules.modalities import urlpatterns as modality_urls
from admin_api.modules.modality_types import urlpatterns as modality_type_urls
from admin_api.modules.nucleos import urlpatterns as nucleos_urls
from admin_api.modules.staff import urlpatterns as staff_urls
from admin_api.modules.teams import urlpatterns as teams_urls
from admin_api.modules.tournaments import urlpatterns as tournament_urls
from django.urls import include, path

urlpatterns = [
    path("admins/", include(admin_urls)),
    path("modality-types/", include(modality_type_urls)),
    path("modalities/", include(modality_urls)),
    path("tournaments/", include(tournament_urls)),
    path("nucleos/", include(nucleos_urls)),
    path("courses/", include(courses_urls)),
    path("athletes/", include(athletes_urls)),
    path("staff/", include(staff_urls)),
    path("matches/", include(matches_urls)),
    path("teams/", include(teams_urls)),
]
