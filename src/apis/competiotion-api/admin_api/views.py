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
        return Response([])

    def post(self, request):
        serializer = NucleoAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response([])

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response([])

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response([])

    def post(self, request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response([])

    def post(self, request):
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
    return Response({"message": "Tournament finished"})


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
        return Response([])

    def post(self, request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response([])

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    return Response(serializer.data)


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
        return Response([])

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)


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
    return Response(serializer.data)


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
    return Response(serializer.data)


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
    return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response([])

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Start a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_start(request, season_id):
    return Response({"message": "Season started"})


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Finish a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_finish(request, season_id):
    return Response({"message": "Season finished"})
