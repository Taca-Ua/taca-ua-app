from django.http import HttpResponse
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_auth,
    require_roles,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum, get_user

from ..selectors import get_match_by_id, get_match_participant_by_id, get_matches_table
from ..service import (
    assign_lineup,
    assign_staff_to_lineup,
    create_match,
    delete_match,
    match_add_occurrence,
    match_delete_occurrence,
    publish_match_results,
    update_lineup,
    update_match,
)
from .filters import MatchListFilterSerializer
from .pdf_generators import (
    DocumentGenerationLackPermissionError,
    document_generation_service,
)
from .serializers import (
    LineupAssignSerializer,
    LineupAssignStaffSerializer,
    LineupUpdateSerializer,
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    MatchPaginatedListSerializer,
    MatchParticipantLineupSerializer,
    MatchPublishResultsSerializer,
    MatchUpdateSerializer,
    OccurrenceCreateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List matches",
        description="Retrieve a list of matches with optional filtering and pagination.",
        tags=["Match Management"],
        parameters=[MatchListFilterSerializer],
        responses={200: MatchPaginatedListSerializer},
    ),
    post=extend_schema(
        summary="Create a match",
        description="Create a new match with the provided details.",
        tags=["Match Management"],
        request=MatchCreateSerializer,
        responses={201: MatchListSerializer},
    ),
)
class MatchListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = MatchListFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        matches = get_matches_table(
            status=serializer.validated_data.get("status"),
            modality_id=serializer.validated_data.get("modality_id"),
            course_id=serializer.validated_data.get("course_id"),
            tournament_id=serializer.validated_data.get("tournament_id"),
            nucleus_id=serializer.validated_data.get("nucleus_id"),
            team_id=serializer.validated_data.get("team_id"),
            date_from=serializer.validated_data.get("date_from"),
            date_to=serializer.validated_data.get("date_to"),
        )

        # apply pagination
        limit = serializer.validated_data.get("limit")
        offset = (
            (serializer.validated_data.get("page") - 1) * limit
            if serializer.validated_data.get("page") and limit
            else None
        )
        pag_matches = (
            matches[offset : offset + limit]
            if offset is not None and limit is not None
            else matches
        )

        response_serializer = MatchPaginatedListSerializer(
            {"matches": pag_matches, "total": matches.count()}
        )
        return Response(response_serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = create_match(
            tournament_id=serializer.validated_data.get("tournament_id"),
            location=serializer.validated_data.get("location"),
            start_time=serializer.validated_data.get("start_time"),
            participants=serializer.validated_data["participants"],
        )

        serializer = MatchListSerializer(get_match_by_id(match.id))
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve match details",
        description="Get detailed information about a specific match, including participants and occurrences.",
        tags=["Match Management"],
    ),
    put=extend_schema(
        summary="Update a match",
        description="Update the details of an existing match.",
        tags=["Match Management"],
        request=MatchUpdateSerializer,
        responses={200: MatchDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete a match",
        description="Remove a match from the system.",
        tags=["Match Management"],
        responses={204: "No Content"},
    ),
)
class MatchDetailView(RoleRequiredMixin, APIView):
    def get(self, request, match_id):
        # extract admin_id from request
        user = get_user(request)
        admin_id = (
            user.user_id if user and RolesEnum.GENERAL_ADMIN not in user.roles else None
        )

        match = get_match_by_id(match_id, context_admin_id=admin_id)
        serializer = MatchDetailSerializer(match)
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = update_match(
            match_id=match_id,
            location=serializer.validated_data.get("location"),
            start_time=serializer.validated_data.get("start_time"),
            status=serializer.validated_data.get("status"),
        )

        # extract admin_id from request
        user = get_user(request)
        admin_id = (
            user.user_id if user and RolesEnum.GENERAL_ADMIN not in user.roles else None
        )

        serializer = MatchDetailSerializer(
            get_match_by_id(match.id, context_admin_id=admin_id)
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, match_id):
        delete_match(match_id)
        return Response(status=204)


@extend_schema(
    summary="Publish match results",
    description="Publish the results of a match, making them visible to users.",
    tags=["Match Management"],
    request=MatchPublishResultsSerializer,
    responses={200: MatchDetailSerializer},
)
@api_view(["POST"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def publish_match_results_view(request, match_id):
    serializer = MatchPublishResultsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    match = publish_match_results(
        match_id=match_id,
        participant_results=serializer.validated_data["participant_results"],
    )

    # extract admin_id from request
    user = get_user(request)
    admin_id = user.user_id if user else None

    serializer = MatchDetailSerializer(
        get_match_by_id(match.id, context_admin_id=admin_id)
    )
    return Response(serializer.data)


# ============= occurrence Management Views =============


@extend_schema(
    request=OccurrenceCreateSerializer,
    responses=MatchDetailSerializer,
    description="Add a occurrence to a match",
    tags=["Match Management"],
)
@api_view(["POST"])
@require_auth
def add_occurrence(request, match_id):
    """Add occurrence to match"""
    serializer = OccurrenceCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_user(request)

    match = match_add_occurrence(
        match_id=match_id,
        occurrence_text=serializer.validated_data["message"],
        admin_id=user.user_id,
    )

    # Pass admin_id to render function
    admin_id = (
        user.user_id if user and RolesEnum.GENERAL_ADMIN not in user.roles else None
    )
    response_serializer = MatchDetailSerializer(
        get_match_by_id(match.id, context_admin_id=admin_id)
    )
    return Response(response_serializer.data, status=201)


@extend_schema(
    responses={204: None},
    description="Delete a occurrence from a match",
    tags=["Match Management"],
)
@api_view(["DELETE"])
@require_auth
def delete_occurrence(request, match_id, occurrence_id):
    """Delete a occurrence"""
    match_delete_occurrence(
        match_id=match_id,
        occurrence_id=occurrence_id,
    )
    return Response(status=204)


# ============= Lineup Management Views =============


@extend_schema_view(
    get=extend_schema(
        responses=MatchParticipantLineupSerializer,
        description="Retrieve lineups for a match",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=LineupAssignSerializer,
        responses=MatchParticipantLineupSerializer,
        description="Assign lineup for a team in a match",
        tags=["Match Management"],
    ),
    put=extend_schema(
        request=LineupUpdateSerializer,
        responses=MatchParticipantLineupSerializer,
        description="Update lineup for a team in a match",
        tags=["Match Management"],
    ),
)
class MatchLineupsView(RoleRequiredMixin, APIView):
    """View to retrieve lineups for a match"""

    def get(self, request, match_id, participant_id):
        """Retrieve lineups for a match"""
        user = get_user(request)
        admin_id = (
            user.user_id if user and RolesEnum.GENERAL_ADMIN not in user.roles else None
        )

        participant = get_match_participant_by_id(
            match_id=match_id, participant_id=participant_id, context_admin_id=admin_id
        )

        serializer = MatchParticipantLineupSerializer(participant)
        return Response(serializer.data)

    def post(self, request, match_id, participant_id):
        """Assign lineup for a team"""
        serializer = LineupAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participant = assign_lineup(
            match_id=match_id,
            participant_id=participant_id,
            players=serializer.validated_data["players"],
        )

        response_serializer = MatchParticipantLineupSerializer(
            get_match_participant_by_id(
                match_id=match_id, participant_id=participant.id
            )
        )
        return Response(response_serializer.data, status=200)

    def put(self, request, match_id, participant_id):
        """Update lineup for a team"""
        serializer = LineupUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participant = update_lineup(
            match_id=match_id,
            participant_id=participant_id,
            players=serializer.validated_data["players"],
        )

        response_serializer = MatchParticipantLineupSerializer(
            get_match_participant_by_id(
                match_id=match_id, participant_id=participant.id
            )
        )
        return Response(response_serializer.data, status=200)


@extend_schema(
    request=LineupAssignStaffSerializer,
    responses=MatchParticipantLineupSerializer,
    description="Assign staff members to a team's lineup",
    tags=["Match Management"],
)
@api_view(["POST"])
@require_auth
def add_staff_to_lineup(request, match_id, participant_id):
    """Assign staff members to a team's lineup"""
    serializer = LineupAssignStaffSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    participant = assign_staff_to_lineup(
        match_id=match_id,
        participant_id=participant_id,
        staff_ids=serializer.validated_data["staff_ids"],
    )

    response_serializer = MatchParticipantLineupSerializer(
        get_match_participant_by_id(match_id=match_id, participant_id=participant.id)
    )
    return Response(response_serializer.data, status=200)


# ============= Document Generation Views =============


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def match_sheet(request, match_id):
    """Generate match sheet PDF"""

    match = get_match_by_id(match_id, include_lineups=True)

    pdf_content = document_generation_service.generate_match_report(match)

    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="match_sheet_{match_id}.pdf"'
    )
    return response


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF for a specific team",
    tags=["Match Management"],
)
@api_view(["GET"])
@require_auth
def match_team_sheet(request, match_id, participant_id):
    """
    Generate match sheet PDF for a specific team in a match.
    """

    match_participant = get_match_participant_by_id(match_id, participant_id)

    try:
        pdf_content = document_generation_service.generate_match_team_report(
            match_participant
        )
    except DocumentGenerationLackPermissionError as e:
        return Response({"detail": str(e)}, status=403)

    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="match_team_sheet_{match_id}_{participant_id}.pdf"'
    )
    return response


urlpatterns = [
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
    path(
        "<uuid:match_id>/results/",
        publish_match_results_view,
        name="match-publish-results",
    ),
    path(
        "<uuid:match_id>/occurrences/",
        add_occurrence,
        name="match-add-occurrence",
    ),
    path(
        "<uuid:match_id>/sheet/",
        match_sheet,
        name="match-sheet",
    ),
    path(
        "<uuid:match_id>/occurrences/<uuid:occurrence_id>/",
        delete_occurrence,
        name="match-delete-occurrence",
    ),
    path(
        "<uuid:match_id>/lineups/<uuid:participant_id>/",
        MatchLineupsView.as_view(),
        name="match-lineups",
    ),
    path(
        "<uuid:match_id>/participants/<uuid:participant_id>/staff/",
        add_staff_to_lineup,
        name="match-assign-staff-lineup",
    ),
    path(
        "<uuid:match_id>/participants/<uuid:participant_id>/sheet/",
        match_team_sheet,
        name="match-team-sheet",
    ),
]
