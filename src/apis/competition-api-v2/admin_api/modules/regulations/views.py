from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegulationCreateSerializer,
    RegulationDetailSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)
from .service import regulations_service


@extend_schema_view(
    get=extend_schema(
        responses=RegulationListSerializer(many=True),
        description="List all regulations from database",
        tags=["Regulation Management"],
    ),
    post=extend_schema(
        request=RegulationCreateSerializer,
        responses=RegulationListSerializer,
        description="Upload a new regulation to MinIO and save to database",
        tags=["Regulation Management"],
    ),
)
class RegulationListCreateView(APIView):
    def get(self, request):
        regulations = regulations_service.list_regulations()

        serializer = RegulationListSerializer(regulations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        regulation = regulations_service.create_regulation(
            title=serializer.validated_data["title"],
            file=serializer.validated_data.pop("file"),
            description=serializer.validated_data.get("description", ""),
        )

        serializer = RegulationListSerializer(regulation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=RegulationDetailSerializer,
        description="Get a single regulation by ID",
        tags=["Regulation Management"],
    ),
    put=extend_schema(
        request=RegulationUpdateSerializer,
        responses=RegulationDetailSerializer,
        description="Update regulation metadata",
        tags=["Regulation Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a regulation from database and storage",
        tags=["Regulation Management"],
    ),
)
class RegulationDetailView(APIView):
    def get(self, request, regulation_id):
        regulation = regulations_service.get_regulation(regulation_id)

        serializer = RegulationDetailSerializer(regulation)
        return Response(serializer.data)

    def put(self, request, regulation_id):
        serializer = RegulationUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        regulation = regulations_service.update_regulation(
            regulation_id=regulation_id,
            file=serializer.validated_data.get("file"),
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
        )

        serializer = RegulationDetailSerializer(regulation)
        return Response(serializer.data)

    def delete(self, request, regulation_id):
        regulations_service.delete_regulation(regulation_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", RegulationListCreateView.as_view(), name="regulation-list-create"),
    path(
        "<str:regulation_id>/", RegulationDetailView.as_view(), name="regulation-detail"
    ),
]
