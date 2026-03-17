from admin_api.modules.admins import urlpatterns as admin_urls
from admin_api.modules.modality_types import urlpatterns as modality_type_urls
from django.urls import include, path

# from .modules.modalities.views import urlpatterns as modality_urls
# from .modules.tournaments.views import urlpatterns as tournament_urls


urlpatterns = [
    path("admins/", include(admin_urls)),
    path("modality-types/", include(modality_type_urls)),
    # path("modalities/", include(modality_urls)),
    # path("tournaments/", include(tournament_urls)),
]
