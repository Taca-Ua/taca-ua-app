"""
Views for file management operations
"""

from admin_api.serializers.file_serializers import (
    FileDeleteSerializer,
    FileUploadResponseSerializer,
    FileUploadSerializer,
)
from admin_api.services.minio_service import MinioService
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


class FileUploadView(APIView):
    """
    API endpoint for uploading files to MinIO storage
    """

    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=FileUploadSerializer,
        responses={
            201: OpenApiResponse(
                response=FileUploadResponseSerializer,
                description="File uploaded successfully",
            ),
            400: OpenApiResponse(description="Invalid request data"),
            500: OpenApiResponse(description="Server error during upload"),
        },
        description="Upload a file to MinIO storage with metadata",
        tags=["Files"],
    )
    def post(self, request):
        """
        Upload a file to MinIO

        Accepts multipart/form-data with:
        - file: The file to upload
        - bucket: The bucket name where the file will be stored

        Returns file hash and public URL
        """
        serializer = FileUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_obj = serializer.validated_data["file"]
        bucket_name = serializer.validated_data["bucket"]

        try:
            # Initialize MinIO service
            minio_service = MinioService()

            # Upload file
            file_hash, object_name, public_url = minio_service.upload_file(
                file_data=file_obj,
                bucket_name=bucket_name,
                original_filename=file_obj.name,
                content_type=file_obj.content_type,
            )

            # Prepare response
            response_data = {
                "file_hash": file_hash,
                "object_name": object_name,
                "bucket": bucket_name,
                "public_url": public_url,
                "content_type": file_obj.content_type,
                "size": file_obj.size,
                "original_filename": file_obj.name,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDeleteView(APIView):
    """
    API endpoint for deleting files from MinIO storage
    """

    @extend_schema(
        request=FileDeleteSerializer,
        responses={
            204: OpenApiResponse(description="File deleted successfully"),
            400: OpenApiResponse(description="Invalid request data"),
            404: OpenApiResponse(description="File not found"),
            500: OpenApiResponse(description="Server error during deletion"),
        },
        description="Delete a file from MinIO storage",
        tags=["Files"],
    )
    def delete(self, request):
        """
        Delete a file from MinIO

        Requires:
        - bucket: The bucket name
        - object_name: The object name to delete
        """
        serializer = FileDeleteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        bucket_name = serializer.validated_data["bucket"]
        object_name = serializer.validated_data["object_name"]

        try:
            # Initialize MinIO service
            minio_service = MinioService()

            # Check if file exists
            if not minio_service.file_exists(bucket_name, object_name):
                return Response(
                    {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Delete file
            minio_service.delete_file(bucket_name, object_name)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
