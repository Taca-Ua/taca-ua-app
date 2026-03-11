"""
URL configuration for admin_api app
Maps endpoints according to API_ENDPOINTS.md specification
"""

from django.urls import include, path

# Reintroduzimos os teus imports (HEAD)
from .views.regulations import RegulationListCreateView, RegulationDetailView

app_name = "admin_api"

urlpatterns = [
    # Authentication (Keycloak)
    path("auth/", include("admin_api.views.auth")),
    # Admin User Management
    path("admins/", include("admin_api.views.admins")),
    # File Management
    path("files/", include("admin_api.views.file_views")),
    # Course Management (RF2)
    path("courses/", include("admin_api.views.courses")),
    
    # Regulation Management (RF2.3) - Tuas rotas mantidas
    path(
        "regulations/", 
        RegulationListCreateView.as_view(), 
        name="regulation-list"
    ),
    path(
        "regulations/<uuid:regulation_id>/", 
        RegulationDetailView.as_view(), 
        name="regulation-detail"
    ),
    
    # Modality Management (RF3)
    path("modalities/", include("admin_api.views.modalities")),
    path("modality-types/", include("admin_api.views.modality_types")),
    # Nucleo Management
    path("nucleos/", include("admin_api.views.nucleus")), # Corrigido para 'nucleus' conforme a dev
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
]