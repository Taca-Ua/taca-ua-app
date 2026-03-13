"""
Regulation management views - Refactored to use Service Layer
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.regulation_service import RegulationService
from ..decorators import RoleRequiredMixin
from ..serializers.regulations import (
    RegulationCreateSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)

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
class RegulationListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        regulations = RegulationService.list_regulations()
        serializer = RegulationListSerializer(regulations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            regulation = RegulationService.create_regulation(
                title=serializer.validated_data['title'],
                file=serializer.validated_data.pop('file'),
                description=serializer.validated_data.get('description', '')
            )
            
            output_serializer = RegulationListSerializer(regulation)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Operation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        responses=RegulationListSerializer,
        description="Get a single regulation by ID",
        tags=["Regulation Management"],
    ),
    put=extend_schema(
        request=RegulationUpdateSerializer,
        responses=RegulationListSerializer,
        description="Update regulation metadata",
        tags=["Regulation Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a regulation from database and storage",
        tags=["Regulation Management"],
    ),
)
class RegulationDetailView(RoleRequiredMixin, APIView):
    def get(self, request, regulation_id):
        regulation = RegulationService.get_regulation(regulation_id)
        serializer = RegulationListSerializer(regulation)
        return Response(serializer.data)

    def put(self, request, regulation_id):
        regulation = RegulationService.get_regulation(regulation_id)
        serializer = RegulationUpdateSerializer(regulation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        output_serializer = RegulationListSerializer(regulation)
        return Response(output_serializer.data)

    def delete(self, request, regulation_id):
        try:
            RegulationService.delete_regulation(regulation_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": f"Failed to delete: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )