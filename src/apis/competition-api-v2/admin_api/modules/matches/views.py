"""
Match management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MatchCreateSerializer, MatchSerializer, MatchUpdateSerializer


@extend_schema_view(
    get=extend_schema(
        responses=MatchSerializer(many=True),
        description="List all matches with optional filters",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=MatchCreateSerializer,
        responses=MatchSerializer,
        description="Create a new match with participants",
        tags=["Match Management"],
    ),
)
class MatchListCreateView(APIView):
    """List and create matches"""

    def get(self, request):
        """List matches with optional filters"""
        return Response(
            {"detail": "List matches with optional filters"}, status=status.HTTP_200_OK
        )

    def post(self, request):
        """Create a new match"""
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Match created successfully"}, status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    get=extend_schema(
        responses=MatchSerializer,
        description="Get detailed information about a specific match",
        tags=["Match Management"],
    ),
    put=extend_schema(
        request=MatchUpdateSerializer,
        responses=MatchSerializer,
        description="Update match metadata (location, start time, status)",
        tags=["Match Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a match",
        tags=["Match Management"],
    ),
)
class MatchDetailView(APIView):
    """Retrieve, update, or delete a match"""

    def get(self, request, match_id):
        """Get match details"""
        return Response({"detail": "Get match details"}, status=status.HTTP_200_OK)

    def put(self, request, match_id):
        """Update match metadata"""
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Match updated successfully"}, status=status.HTTP_200_OK
        )

    def delete(self, request, match_id):
        """Delete a match"""
        return Response(
            {"detail": "Match deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


urlpatterns = [
    # Match CRUD
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
]
