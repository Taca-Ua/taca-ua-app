from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..queries import get_match_by_id, list_matches
from ..service import create_match, delete_match, update_match
from .filters import MatchListFilterSerializer
from .renders import render_match_detail, render_match_list
from .serializers import (
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    MatchPaginatedListSerializer,
    MatchUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List matches",
        description="Retrieve a list of matches with optional filtering and pagination.",
        parameters=[MatchListFilterSerializer],
        responses={200: MatchPaginatedListSerializer},
    ),
    post=extend_schema(
        summary="Create a match",
        description="Create a new match with the provided details.",
        request=MatchCreateSerializer,
        responses={201: MatchListSerializer},
    ),
)
class MatchListCreateView(APIView):
    def get(self, request):
        serializer = MatchListFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        matches = list_matches(
            status=serializer.validated_data.get("status"),
            modality_id=serializer.validated_data.get("modality_id"),
            page_size=serializer.validated_data.get("limit"),
            offset=(
                (serializer.validated_data.get("page") - 1)
                * serializer.validated_data.get("limit")
                if serializer.validated_data.get("page")
                and serializer.validated_data.get("limit")
                else None
            ),
        )

        rm = render_match_list(matches).all()

        response_serializer = MatchPaginatedListSerializer(
            {"matches": rm, "total": matches.count()}
        )
        return Response(response_serializer.data)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = create_match(
            tournament_id=serializer.validated_data.get("tournament_id"),
            location=serializer.validated_data.get("location"),
            start_time=serializer.validated_data.get("start_time"),
            participants=serializer.validated_data["participants"],
            journey=serializer.validated_data.get("journey"),
            new_journey=serializer.validated_data.get("new_journey", False),
        )

        serializer = MatchListSerializer(render_match_list(match).first())
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve match details",
        description="Get detailed information about a specific match, including participants and comments.",
    ),
    put=extend_schema(
        summary="Update a match",
        description="Update the details of an existing match.",
        request=MatchUpdateSerializer,
        responses={200: MatchDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete a match",
        description="Remove a match from the system.",
        responses={204: "No Content"},
    ),
)
class MatchDetailView(APIView):
    def get(self, request, match_id):
        match = get_match_by_id(match_id)

        serializer = MatchDetailSerializer(render_match_detail(match).first())
        return Response(serializer.data)

    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = update_match(
            match_id=match_id,
            location=serializer.validated_data.get("location"),
            start_time=serializer.validated_data.get("start_time"),
            status=serializer.validated_data.get("status"),
        )

        serializer = MatchDetailSerializer(render_match_detail(match).first())
        return Response(serializer.data)

    def delete(self, request, match_id):
        delete_match(match_id)
        return Response(status=204)


urlpatterns = [
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
]
