"""
Views for Competition API (Admin API)
Placeholder views for OpenAPI schema generation
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CourseCreateSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
    MatchCommentSerializer,
    MatchCreateSerializer,
    MatchLineupSerializer,
    MatchListSerializer,
    MatchResultSerializer,
    MatchUpdateSerializer,
    ModalityCreateSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
    NucleoAdminCreateSerializer,
    NucleoAdminListSerializer,
    NucleoAdminUpdateSerializer,
    RegulationCreateSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
    SeasonCreateSerializer,
    SeasonListSerializer,
    StudentCreateSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
    TeamCreateSerializer,
    TeamListSerializer,
    TeamUpdateSerializer,
    TournamentCreateSerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)

# ================== 1. User Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=NucleoAdminListSerializer(many=True),
        description="List nucleo administrators",
        tags=["User Management"],
    ),
    post=extend_schema(
        request=NucleoAdminCreateSerializer,
        responses=NucleoAdminListSerializer,
        description="Create nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "username": "admin_mect",
                "email": "admin@mect.ua.pt",
                "course_id": 1,
                "full_name": "João Silva",
            },
            {
                "id": 2,
                "username": "admin_lei",
                "email": "admin@lei.ua.pt",
                "course_id": 2,
                "full_name": "Maria Santos",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = NucleoAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 3, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=NucleoAdminUpdateSerializer,
        responses=NucleoAdminListSerializer,
        description="Update nucleo administrator",
        tags=["User Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminDetailView(APIView):
    def put(self, request, user_id):
        serializer = NucleoAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": user_id,
            "username": f"admin_user_{user_id}",
            "email": f"admin{user_id}@example.pt",
            **serializer.validated_data,
        }
        return Response(dummy_response)

    def delete(self, request, user_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================== 2. Course Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=CourseListSerializer(many=True),
        description="List all courses",
        tags=["Course Management"],
    ),
    post=extend_schema(
        request=CourseCreateSerializer,
        responses=CourseListSerializer,
        description="Create a new course",
        tags=["Course Management"],
    ),
)
class CourseListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "name": "Engenharia de Computadores e Telemática",
                "short_code": "MECT",
                "color": "#FF5733",
            },
            {
                "id": 2,
                "name": "Engenharia Informática",
                "short_code": "LEI",
                "color": "#33FF57",
            },
            {
                "id": 3,
                "name": "Engenharia Eletrónica e Telecomunicações",
                "short_code": "MIEET",
                "color": "#3357FF",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=CourseUpdateSerializer,
        responses=CourseListSerializer,
        description="Update a course",
        tags=["Course Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a course",
        tags=["Course Management"],
    ),
)
class CourseDetailView(APIView):
    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": course_id,
            "name": serializer.validated_data.get("name", f"Course {course_id}"),
            "short_code": serializer.validated_data.get("short_code", f"C{course_id}"),
            "color": serializer.validated_data.get("color", "#000000"),
        }
        return Response(dummy_response)

    def delete(self, request, course_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================== 3. Regulation Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=RegulationListSerializer(many=True),
        description="List all regulations",
        tags=["Regulation Management"],
    ),
    post=extend_schema(
        request=RegulationCreateSerializer,
        responses=RegulationListSerializer,
        description="Upload a new regulation",
        tags=["Regulation Management"],
    ),
)
class RegulationListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "title": "Regulamento Futebol",
                "description": "Regras do futebol TACA",
                "modality_id": 1,
                "file_url": "http://example.com/reg1.pdf",
                "created_at": "2025-01-15T10:00:00Z",
            },
            {
                "id": 2,
                "title": "Regulamento Futsal",
                "description": "Regras do futsal TACA",
                "modality_id": 2,
                "file_url": "http://example.com/reg2.pdf",
                "created_at": "2025-01-20T10:00:00Z",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": 3,
            "title": serializer.validated_data.get("title"),
            "description": serializer.validated_data.get("description", ""),
            "modality_id": serializer.validated_data.get("modality_id"),
            "file_url": "http://example.com/reg3.pdf",
            "created_at": "2025-12-01T12:00:00Z",
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=RegulationUpdateSerializer,
        responses=RegulationListSerializer,
        description="Update regulation metadata",
        tags=["Regulation Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a regulation",
        tags=["Regulation Management"],
    ),
)
class RegulationDetailView(APIView):
    def put(self, request, regulation_id):
        serializer = RegulationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": regulation_id,
            "title": serializer.validated_data.get(
                "title", f"Regulation {regulation_id}"
            ),
            "description": serializer.validated_data.get("description", ""),
            "modality_id": serializer.validated_data.get("modality_id"),
            "file_url": f"http://example.com/reg{regulation_id}.pdf",
            "created_at": "2025-12-01T12:00:00Z",
        }
        return Response(dummy_response)

    def delete(self, request, regulation_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================== 4. Modality Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=ModalityListSerializer(many=True),
        description="List all modalities",
        tags=["Modality Management"],
    ),
    post=extend_schema(
        request=ModalityCreateSerializer,
        responses=ModalityListSerializer,
        description="Create a new modality",
        tags=["Modality Management"],
    ),
)
class ModalityListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "name": "Futebol",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "id": 2,
                "name": "Futsal",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "id": 3,
                "name": "Ténis",
                "type": "individual",
                "scoring_schema": {"win": 2, "loss": 0},
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=ModalityUpdateSerializer,
        responses=ModalityListSerializer,
        description="Update a modality",
        tags=["Modality Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a modality",
        tags=["Modality Management"],
    ),
)
class ModalityDetailView(APIView):
    def put(self, request, modality_id):
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": modality_id,
            "name": serializer.validated_data.get("name", f"Modality {modality_id}"),
            "type": serializer.validated_data.get("type", "coletiva"),
            "scoring_schema": serializer.validated_data.get(
                "scoring_schema", {"win": 3, "draw": 1, "loss": 0}
            ),
        }
        return Response(dummy_response)

    def delete(self, request, modality_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================== 5. Tournament Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=TournamentListSerializer(many=True),
        description="List all tournaments",
        tags=["Tournament Management"],
    ),
    post=extend_schema(
        request=TournamentCreateSerializer,
        responses=TournamentListSerializer,
        description="Create a new tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "modality_id": 1,
                "name": "Campeonato Futebol 2025",
                "season_id": 1,
                "rules": "Formato eliminatória",
                "status": "active",
                "start_date": "2025-02-01T10:00:00Z",
                "teams": [1, 2, 3],
            },
            {
                "id": 2,
                "modality_id": 2,
                "name": "Campeonato Futsal 2025",
                "season_id": 1,
                "rules": "Todos contra todos",
                "status": "draft",
                "start_date": None,
                "teams": [],
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 3, "status": "draft", **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=TournamentUpdateSerializer,
        responses=TournamentListSerializer,
        description="Update a tournament",
        tags=["Tournament Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentDetailView(APIView):
    def put(self, request, tournament_id):
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": tournament_id,
            "modality_id": 1,
            "name": serializer.validated_data.get(
                "name", f"Tournament {tournament_id}"
            ),
            "season_id": 1,
            "rules": serializer.validated_data.get("rules", ""),
            "status": "active",
            "start_date": serializer.validated_data.get("start_date"),
            "teams": serializer.validated_data.get("teams", []),
        }
        return Response(dummy_response)

    def delete(self, request, tournament_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=None,
    responses={200: TournamentListSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
def tournament_finish(request, tournament_id):
    dummy_response = {
        "id": tournament_id,
        "modality_id": 1,
        "name": f"Tournament {tournament_id}",
        "season_id": 1,
        "rules": "Competition rules",
        "status": "finished",
        "start_date": "2025-02-01T10:00:00Z",
        "teams": [1, 2, 3, 4],
    }
    return Response(dummy_response)


# ================== 6. Team Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=TeamListSerializer(many=True),
        description="List all teams",
        tags=["Team Management"],
    ),
    post=extend_schema(
        request=TeamCreateSerializer,
        responses=TeamListSerializer,
        description="Create a new team",
        tags=["Team Management"],
    ),
)
class TeamListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "modality_id": 1,
                "course_id": 1,
                "name": "MECT A",
                "players": [1, 2, 3, 4, 5],
            },
            {
                "id": 2,
                "modality_id": 1,
                "course_id": 2,
                "name": "LEI A",
                "players": [6, 7, 8, 9, 10],
            },
            {
                "id": 3,
                "modality_id": 2,
                "course_id": 1,
                "name": "MECT Futsal",
                "players": [1, 2, 11, 12],
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "course_id": 1, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=TeamUpdateSerializer,
        responses=TeamListSerializer,
        description="Update a team",
        tags=["Team Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a team",
        tags=["Team Management"],
    ),
)
class TeamDetailView(APIView):
    def put(self, request, team_id):
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_players = [1, 2, 3]
        players_add = serializer.validated_data.get("players_add", [])
        players_remove = serializer.validated_data.get("players_remove", [])
        updated_players = [
            p for p in current_players if p not in players_remove
        ] + players_add
        dummy_response = {
            "id": team_id,
            "modality_id": 1,
            "course_id": 1,
            "name": serializer.validated_data.get("name", f"Team {team_id}"),
            "players": updated_players,
        }
        return Response(dummy_response)

    def delete(self, request, team_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================== 7. Student Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=StudentListSerializer(many=True),
        description="List all students of the course",
        tags=["Student Management"],
    ),
    post=extend_schema(
        request=StudentCreateSerializer,
        responses=StudentListSerializer,
        description="Create a new student",
        tags=["Student Management"],
    ),
)
class StudentListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "course_id": 1,
                "full_name": "João Silva",
                "student_number": "100001",
                "email": "joao@ua.pt",
                "is_member": True,
            },
            {
                "id": 2,
                "course_id": 1,
                "full_name": "Maria Santos",
                "student_number": "100002",
                "email": "maria@ua.pt",
                "is_member": True,
            },
            {
                "id": 3,
                "course_id": 2,
                "full_name": "Pedro Costa",
                "student_number": "100003",
                "email": "pedro@ua.pt",
                "is_member": False,
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "course_id": 1, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    request=StudentUpdateSerializer,
    responses=StudentListSerializer,
    description="Update a student",
    tags=["Student Management"],
)
@api_view(["PUT"])
def student_update(request, student_id):
    serializer = StudentUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": student_id,
        "course_id": 1,
        "full_name": serializer.validated_data.get(
            "full_name", f"Student {student_id}"
        ),
        "student_number": f"10000{student_id}",
        "email": serializer.validated_data.get("email", f"student{student_id}@ua.pt"),
        "is_member": serializer.validated_data.get("is_member", False),
    }
    return Response(dummy_response)


# ================== 8. Match Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=MatchListSerializer(many=True),
        description="List all matches",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=MatchCreateSerializer,
        responses=MatchListSerializer,
        description="Create a new match",
        tags=["Match Management"],
    ),
)
class MatchListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "tournament_id": 1,
                "team_home_id": 1,
                "team_away_id": 2,
                "location": "Campo 1",
                "start_time": "2025-02-10T15:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            {
                "id": 2,
                "tournament_id": 1,
                "team_home_id": 1,
                "team_away_id": 3,
                "location": "Campo 2",
                "start_time": "2025-02-15T16:00:00Z",
                "status": "finished",
                "home_score": 3,
                "away_score": 1,
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": 3,
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
            **serializer.validated_data,
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=MatchUpdateSerializer,
        responses=MatchListSerializer,
        description="Update a match",
        tags=["Match Management"],
    ),
)
class MatchDetailView(APIView):
    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": match_id,
            "tournament_id": 1,
            "team_home_id": serializer.validated_data.get("team_home_id", 1),
            "team_away_id": serializer.validated_data.get("team_away_id", 2),
            "location": serializer.validated_data.get("location", "Campo 1"),
            "start_time": serializer.validated_data.get(
                "start_time", "2025-02-10T15:00:00Z"
            ),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        }
        return Response(dummy_response)


@extend_schema(
    request=MatchResultSerializer,
    responses=MatchListSerializer,
    description="Register match result",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_result(request, match_id):
    serializer = MatchResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": match_id,
        "tournament_id": 1,
        "team_home_id": 1,
        "team_away_id": 2,
        "location": "Campo 1",
        "start_time": "2025-02-10T15:00:00Z",
        "status": "finished",
        **serializer.validated_data,
    }
    return Response(dummy_response)


@extend_schema(
    request=MatchLineupSerializer,
    responses={200: None},
    description="Assign players to match lineup",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_lineup(request, match_id):
    serializer = MatchLineupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "match_id": match_id,
        "team_id": serializer.validated_data.get("team_id"),
        "players": serializer.validated_data.get("players"),
        "message": "Lineup assigned successfully",
    }
    return Response(dummy_response)


@extend_schema(
    request=MatchCommentSerializer,
    responses={201: None},
    description="Add comments to match",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_comments(request, match_id):
    serializer = MatchCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": 1,
        "match_id": match_id,
        "message": serializer.validated_data.get("message"),
        "created_at": "2025-12-01T12:00:00Z",
        "author": "Admin User",
    }
    return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_sheet(request, match_id):
    return Response({"message": "PDF generation not implemented"})


# ================== 9. Season Management ==================


@extend_schema_view(
    get=extend_schema(
        responses=SeasonListSerializer(many=True),
        description="List all seasons",
        tags=["Season Management"],
    ),
    post=extend_schema(
        request=SeasonCreateSerializer,
        responses=SeasonListSerializer,
        description="Create a new season",
        tags=["Season Management"],
    ),
)
class SeasonListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {"id": 1, "year": 2024, "status": "finished"},
            {"id": 2, "year": 2025, "status": "active"},
            {"id": 3, "year": 2026, "status": "draft"},
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "status": "draft", **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Start a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_start(request, season_id):
    dummy_response = {"id": season_id, "year": 2025, "status": "active"}
    return Response(dummy_response)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Finish a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_finish(request, season_id):
    dummy_response = {"id": season_id, "year": 2025, "status": "finished"}
    return Response(dummy_response)
