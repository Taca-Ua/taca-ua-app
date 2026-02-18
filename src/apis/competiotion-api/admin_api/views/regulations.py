"""
Regulation management views
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Regulation
from ..services.file_service import FileService
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
class RegulationListCreateView(APIView):
    def get(self, request):
        regulations = Regulation.objects.all()
        serializer = RegulationListSerializer(regulations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_service = FileService()
        try:
            # Upload real para o MinIO
            upload_data = file_service.upload_file(
                file=serializer.validated_data.pop('file')
            )
            
            # Persistência no Postgres
            regulation = Regulation.objects.create(
                title=serializer.validated_data.get('title'),
                description=serializer.validated_data.get('description', ''),
                modality_id=serializer.validated_data.get('modality_id'),
                file_url=upload_data['file_url']
            )
            
            output_serializer = RegulationListSerializer(regulation)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to upload or save regulation: {str(e)}"}, 
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
class RegulationDetailView(APIView):
    def get(self, request, regulation_id):
        regulation = get_object_or_404(Regulation, id=regulation_id)
        serializer = RegulationListSerializer(regulation)
        return Response(serializer.data)

    def put(self, request, regulation_id):
        regulation = get_object_or_404(Regulation, id=regulation_id)
        serializer = RegulationUpdateSerializer(regulation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        output_serializer = RegulationListSerializer(regulation)
        return Response(output_serializer.data)

    def delete(self, request, regulation_id):
        regulation = get_object_or_404(Regulation, id=regulation_id)
        regulation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)