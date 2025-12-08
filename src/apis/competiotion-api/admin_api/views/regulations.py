"""
Regulation management views with MinIO integration
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    RegulationCreateSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)
from ..service.storage_service import MinIOStorageService


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
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = MinIOStorageService()

    def get(self, request):
        # TODO: Replace with actual database query
        dummy_data = [
            {
                "id": 1,
                "title": "Regulamento Futebol",
                "description": "Regras do futebol TACA",
                "modality_id": 1,
                "file_url": "http://localhost:9000/regulations/abc123.pdf",
                "file_hash": "abc123",
                "created_at": "2025-01-15T10:00:00Z",
            },
            {
                "id": 2,
                "title": "Regulamento Futsal",
                "description": "Regras do futsal TACA",
                "modality_id": 2,
                "file_url": "http://localhost:9000/regulations/def456.pdf",
                "file_hash": "def456",
                "created_at": "2025-01-20T10:00:00Z",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get uploaded file
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Read file content
        file_content = uploaded_file.read()

        # Upload to MinIO
        try:
            upload_result = self.storage.upload_file(
                file_content=file_content,
                original_filename=uploaded_file.name,
                content_type=uploaded_file.content_type or "application/pdf",
            )

            # TODO: Save to database
            # regulation = Regulation.objects.create(
            #     title=serializer.validated_data.get("title"),
            #     description=serializer.validated_data.get("description", ""),
            #     modality_id=serializer.validated_data.get("modality_id"),
            #     file_url=upload_result["url"],
            #     file_hash=upload_result["hash"],
            #     file_size=upload_result["size"],
            # )

            response_data = {
                "id": 3,  # TODO: Use actual ID from database
                "title": serializer.validated_data.get("title"),
                "description": serializer.validated_data.get("description", ""),
                "modality_id": serializer.validated_data.get("modality_id"),
                "file_url": upload_result["url"],
                "file_hash": upload_result["hash"],
                "file_size": upload_result["size"],
                "already_exists": upload_result.get("already_exists", False),
                "created_at": "2025-12-08T12:00:00Z",
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to upload file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        description="Delete a regulation",
        tags=["Regulation Management"],
    ),
)
class RegulationDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = MinIOStorageService()

    def get(self, request, regulation_id):
        # TODO: Replace with actual database query
        all_regulations = [
            {
                "id": 1,
                "title": "Regulamento Futebol",
                "description": "Regras do futebol TACA",
                "modality_id": 1,
                "file_url": "http://localhost:9000/regulations/abc123.pdf",
                "file_hash": "abc123",
                "created_at": "2025-01-15T10:00:00Z",
            },
            {
                "id": 2,
                "title": "Regulamento Futsal",
                "description": "Regras do futsal TACA",
                "modality_id": 2,
                "file_url": "http://localhost:9000/regulations/def456.pdf",
                "file_hash": "def456",
                "created_at": "2025-01-20T10:00:00Z",
            },
        ]

        regulation = next(
            (r for r in all_regulations if r["id"] == regulation_id), None
        )

        if regulation is None:
            return Response(
                {"error": "Regulation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(regulation)

    def put(self, request, regulation_id):
        serializer = RegulationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if new file is being uploaded
        uploaded_file = request.FILES.get("file")
        file_data = {}

        if uploaded_file:
            try:
                file_content = uploaded_file.read()
                upload_result = self.storage.upload_file(
                    file_content=file_content,
                    original_filename=uploaded_file.name,
                    content_type=uploaded_file.content_type or "application/pdf",
                )
                file_data = {
                    "file_url": upload_result["url"],
                    "file_hash": upload_result["hash"],
                    "file_size": upload_result["size"],
                }
            except Exception as e:
                return Response(
                    {"error": f"Failed to upload file: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # TODO: Update in database
        response_data = {
            "id": regulation_id,
            "title": serializer.validated_data.get(
                "title", f"Regulation {regulation_id}"
            ),
            "description": serializer.validated_data.get("description", ""),
            "modality_id": serializer.validated_data.get("modality_id"),
            **file_data,  # Include new file data if uploaded
            "created_at": "2025-12-01T12:00:00Z",
        }

        # Set defaults if no new file
        if not uploaded_file:
            response_data.setdefault(
                "file_url", f"http://localhost:9000/regulations/reg{regulation_id}.pdf"
            )
            response_data.setdefault("file_hash", f"hash{regulation_id}")

        return Response(response_data)

    def delete(self, request, regulation_id):
        # TODO: Get regulation from database and delete file
        # regulation = Regulation.objects.get(id=regulation_id)
        # if regulation.file_hash:
        #     filename = f"{regulation.file_hash}.pdf"
        #     self.storage.delete_file(filename)
        # regulation.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
