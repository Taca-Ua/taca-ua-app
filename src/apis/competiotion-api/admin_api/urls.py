"""
URL configuration for admin_api app
Maps endpoints according to API_ENDPOINTS.md specification
"""

from django.urls import include, path

from .views.users import (
    AdministratorDetailView,
    AdministratorListCreateView,
    NucleoAdminDetailView,
    NucleoAdminListCreateView,
)

app_name = "admin_api"

urlpatterns = [
    # Authentication (temporary!)
    path("auth/", include("admin_api.views.auth")),
    # File Management
    path("files/", include("admin_api.views.file_views")),
    # Administrator Management
    path(
        "administrators/",
        AdministratorListCreateView.as_view(),
        name="administrator-list",
    ),
    path(
        "administrators/<admin_id>/",
        AdministratorDetailView.as_view(),
        name="administrator-detail",
    ),
    # User Management (RF1)
    path(
        "users/nucleo/",
        NucleoAdminListCreateView.as_view(),
        name="nucleo-admin-list",
    ),
    path(
        "users/nucleo/<user_id>/",
        NucleoAdminDetailView.as_view(),
        name="nucleo-admin-detail",
    ),
    # Course Management (RF2)
    path("courses/", include("admin_api.views.courses")),
    # Regulation Management (RF2.3)
    path("regulations/", include("admin_api.views.regulations")),
    # Modality Management (RF3)
    path("modalities/", include("admin_api.views.modalities")),
    path("modality-types/", include("admin_api.views.modalities_types")),
    # Nucleo Management
    path("nucleos/", include("admin_api.views.nucleus")),
    # Tournament Management (RF3)
    path("tournaments/", include("admin_api.views.tournaments")),
    # Team Management (RF4)
    path("teams/", include("admin_api.views.teams")),
    # Student Management (RF4)
    path("students/", include("admin_api.views.students")),
    # Staff Management
    path("staff/", include("admin_api.views.staff")),
    # Match Management (RF7)
    path("matches/", include("admin_api.views.matches")),
    # Season Management (RF2.4)
    path("seasons/", include("admin_api.views.seasons")),
    # Public API
    path("public/", include("admin_api.views.public")),
]
