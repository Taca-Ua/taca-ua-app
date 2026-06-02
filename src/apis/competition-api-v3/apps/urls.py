from apps.views import HealthView
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .athletes.api.views import urlpatterns as athletes_urlpatterns
from .courses.api.views import urlpatterns as courses_urlpatterns
from .modalities.api.views import urlpatterns as modalities_urlpatterns
from .modality_types.api.views import urlpatterns as modality_types_urlpatterns
from .nucleus.api.views import urlpatterns as nucleus_urlpatterns
from .seasons.api.views import urlpatterns as seasons_urlpatterns
from .staff.api.views import urlpatterns as staff_urlpatterns

urlpatterns = [
    path("athletes/", include(athletes_urlpatterns)),
    path("courses/", include(courses_urlpatterns)),
    path("modalities/", include(modalities_urlpatterns)),
    path("nucleos/", include(nucleus_urlpatterns)),
    path("modality-types/", include(modality_types_urlpatterns)),
    path("seasons/", include(seasons_urlpatterns)),
    path("staff/", include(staff_urlpatterns)),
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
