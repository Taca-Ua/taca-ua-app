from apps.views import HealthView
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .admins.api.views import urlpatterns as admins_urlpatterns
from .athletes.api.views import urlpatterns as athletes_urlpatterns
from .courses.api.views import urlpatterns as courses_urlpatterns
from .matches.api.views import urlpatterns as matches_urlpatterns
from .modalities.api.views import urlpatterns as modalities_urlpatterns
from .modality_types.api.views import urlpatterns as modality_types_urlpatterns
from .nucleus.api.views import urlpatterns as nucleus_urlpatterns
from .ranking.api.views import urlpatterns as ranking_urlpatterns
from .regulations.api.views import urlpatterns as regulations_urlpatterns
from .seasons.api.views import urlpatterns as seasons_urlpatterns
from .staff.api.views import urlpatterns as staff_urlpatterns
from .teams.api.views import urlpatterns as teams_urlpatterns
from .tournaments.api.views import urlpatterns as tournaments_urlpatterns

urlpatterns = [
    path("admins/", include(admins_urlpatterns)),
    path("athletes/", include(athletes_urlpatterns)),
    path("courses/", include(courses_urlpatterns)),
    path("modalities/", include(modalities_urlpatterns)),
    path("nucleos/", include(nucleus_urlpatterns)),
    path("ranking/", include(ranking_urlpatterns)),
    path("modality-types/", include(modality_types_urlpatterns)),
    path("regulations/", include(regulations_urlpatterns)),
    path("seasons/", include(seasons_urlpatterns)),
    path("staff/", include(staff_urlpatterns)),
    path("teams/", include(teams_urlpatterns)),
    path("tournaments/", include(tournaments_urlpatterns)),
    path("matches/", include(matches_urlpatterns)),
]

# Basic URL patterns for the API, including health check and documentation endpoints
urlpatterns += [
    # Health check endpoint
    path("health/", HealthView.as_view(), name="health"),
    # API schema and documentation endpoints
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
