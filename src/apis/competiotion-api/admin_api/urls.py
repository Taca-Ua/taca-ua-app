"""
URL configuration for admin_api app
Maps endpoints according to API_ENDPOINTS.md specification
"""

from django.urls import path

from . import views
from .views.file_views import FileDeleteView, FileUploadView

app_name = "admin_api"

urlpatterns = [
    # Authentication (temporary!)
    path("auth/login", views.login, name="auth-login"),
    path("auth/logout", views.logout, name="auth-logout"),
    path("auth/me", views.me, name="auth-me"),
    # File Management
    path("files/upload", FileUploadView.as_view(), name="file-upload"),
    path("files/delete", FileDeleteView.as_view(), name="file-delete"),
    # Administrator Management
    path(
        "administrators",
        views.AdministratorListCreateView.as_view(),
        name="administrator-list",
    ),
    path(
        "administrators/<admin_id>",
        views.AdministratorDetailView.as_view(),
        name="administrator-detail",
    ),
    # User Management (RF1)
    path(
        "users/nucleo",
        views.NucleoAdminListCreateView.as_view(),
        name="nucleo-admin-list",
    ),
    path(
        "users/nucleo/<user_id>",
        views.NucleoAdminDetailView.as_view(),
        name="nucleo-admin-detail",
    ),
    # Course Management (RF2)
    path("courses", views.CourseListCreateView.as_view(), name="course-list"),
    path(
        "courses/<course_id>",
        views.CourseDetailView.as_view(),
        name="course-detail",
    ),
    # Regulation Management (RF2.3)
    path(
        "regulations", views.RegulationListCreateView.as_view(), name="regulation-list"
    ),
    path(
        "regulations/<regulation_id>",
        views.RegulationDetailView.as_view(),
        name="regulation-detail",
    ),
    # Modality Management (RF3)
    path("modalities", views.ModalityListCreateView.as_view(), name="modality-list"),
    path(
        "modalities/<modality_id>",
        views.ModalityDetailView.as_view(),
        name="modality-detail",
    ),
    path(
        "modality-types",
        views.ModalityTypeListCreateView.as_view(),
        name="modality-type-list",
    ),
    path(
        "modality-types/<modality_type_id>",
        views.ModalityTypeDetailView.as_view(),
        name="modality-type-detail",
    ),
    # Nucleo Management
    path("nucleos", views.NucleoListCreateView.as_view(), name="nucleo-list"),
    path(
        "nucleos/<nucleo_id>",
        views.NucleoDetailView.as_view(),
        name="nucleo-detail",
    ),
    # Tournament Management (RF3)
    path(
        "tournaments", views.TournamentListCreateView.as_view(), name="tournament-list"
    ),
    path(
        "tournaments/<tournament_id>",
        views.TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
    path(
        "tournaments/<tournament_id>/finish",
        views.tournament_finish,
        name="tournament-finish",
    ),
    # Team Management (RF4)
    path("teams", views.TeamListCreateView.as_view(), name="team-list"),
    path("teams/<team_id>", views.TeamDetailView.as_view(), name="team-detail"),
    # Student Management (RF4)
    path("students", views.StudentListCreateView.as_view(), name="student-list"),
    path(
        "students/<student_id>",
        views.StudentDetailView.as_view(),
        name="student-detail",
    ),
    # Staff Management
    path("staff", views.StaffListCreateView.as_view(), name="staff-list"),
    path("staff/<staff_id>", views.StaffDetailView.as_view(), name="staff-detail"),
    # Match Management (RF7)
    path("matches", views.MatchListCreateView.as_view(), name="match-list"),
    path("matches/<match_id>", views.MatchDetailView.as_view(), name="match-detail"),
    path("matches/<match_id>/result", views.match_result, name="match-result"),
    path("matches/<match_id>/lineup", views.match_lineup, name="match-lineup"),
    path("matches/<match_id>/comments", views.match_comments, name="match-comments"),
    path("matches/<match_id>/sheet", views.match_sheet, name="match-sheet"),
    # Season Management (RF2.4)
    path("seasons", views.SeasonListCreateView.as_view(), name="season-list"),
    path("seasons/<season_id>/start", views.season_start, name="season-start"),
    path("seasons/<season_id>/finish", views.season_finish, name="season-finish"),
    # Public API
    path("public/matches", views.calendar, name="public-calendar"),
    path("public/modalities", views.modality_list, name="public-modality-list"),
]
