"""
URL configuration for admin_api app
Maps endpoints according to API_ENDPOINTS.md specification
"""

from django.urls import path

from . import views

app_name = "admin_api"

urlpatterns = [
    # User Management (RF1)
    path(
        "users/nucleo",
        views.NucleoAdminListCreateView.as_view(),
        name="nucleo-admin-list",
    ),
    path(
        "users/nucleo/<int:user_id>",
        views.NucleoAdminDetailView.as_view(),
        name="nucleo-admin-detail",
    ),
    # Course Management (RF2)
    path("courses", views.CourseListCreateView.as_view(), name="course-list"),
    path(
        "courses/<int:course_id>",
        views.CourseDetailView.as_view(),
        name="course-detail",
    ),
    # Regulation Management (RF2.3)
    path(
        "regulations", views.RegulationListCreateView.as_view(), name="regulation-list"
    ),
    path(
        "regulations/<int:regulation_id>",
        views.RegulationDetailView.as_view(),
        name="regulation-detail",
    ),
    # Modality Management (RF3)
    path("modalities", views.ModalityListCreateView.as_view(), name="modality-list"),
    path(
        "modalities/<int:modality_id>",
        views.ModalityDetailView.as_view(),
        name="modality-detail",
    ),
    # Tournament Management (RF3)
    path(
        "tournaments", views.TournamentListCreateView.as_view(), name="tournament-list"
    ),
    path(
        "tournaments/<int:tournament_id>",
        views.TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
    path(
        "tournaments/<int:tournament_id>/finish",
        views.tournament_finish,
        name="tournament-finish",
    ),
    # Team Management (RF4)
    path("teams", views.TeamListCreateView.as_view(), name="team-list"),
    path("teams/<int:team_id>", views.TeamDetailView.as_view(), name="team-detail"),
    # Student Management (RF4)
    path("students", views.StudentListCreateView.as_view(), name="student-list"),
    path("students/<int:student_id>", views.student_update, name="student-update"),
    # Match Management (RF7)
    path("matches", views.MatchListCreateView.as_view(), name="match-list"),
    path(
        "matches/<int:match_id>", views.MatchDetailView.as_view(), name="match-detail"
    ),
    path("matches/<int:match_id>/result", views.match_result, name="match-result"),
    path("matches/<int:match_id>/lineup", views.match_lineup, name="match-lineup"),
    path(
        "matches/<int:match_id>/comments", views.match_comments, name="match-comments"
    ),
    path("matches/<int:match_id>/sheet", views.match_sheet, name="match-sheet"),
    # Season Management (RF2.4)
    path("seasons", views.SeasonListCreateView.as_view(), name="season-list"),
    path("seasons/<int:season_id>/start", views.season_start, name="season-start"),
    path("seasons/<int:season_id>/finish", views.season_finish, name="season-finish"),
]
