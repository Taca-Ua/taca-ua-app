"""
Serializers for file upload operations
"""

from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload request"""

    file = serializers.FileField(required=True, help_text="File to upload")
    bucket = serializers.CharField(
        required=True,
        max_length=63,
        help_text="Bucket name where the file will be stored",
    )

    def validate_bucket(self, value):
        """Validate bucket name follows MinIO naming conventions"""
        if not value:
            raise serializers.ValidationError("Bucket name cannot be empty")

        # MinIO bucket naming rules
        if len(value) < 3 or len(value) > 63:
            raise serializers.ValidationError(
                "Bucket name must be between 3 and 63 characters"
            )

        if not value.replace("-", "").replace(".", "").isalnum():
            raise serializers.ValidationError(
                "Bucket name can only contain lowercase letters, numbers, dots, and hyphens"
            )

        if not value[0].isalnum() or not value[-1].isalnum():
            raise serializers.ValidationError(
                "Bucket name must start and end with a letter or number"
            )

        return value.lower()


class FileUploadResponseSerializer(serializers.Serializer):
    """Serializer for file upload response"""

    file_hash = serializers.CharField(help_text="SHA256 hash of the uploaded file")
    object_name = serializers.CharField(help_text="Name of the object in MinIO storage")
    bucket = serializers.CharField(help_text="Bucket where the file is stored")
    public_url = serializers.URLField(help_text="Public URL to access the file")
    content_type = serializers.CharField(help_text="MIME type of the uploaded file")
    size = serializers.IntegerField(help_text="Size of the file in bytes")
    original_filename = serializers.CharField(help_text="Original filename")


class FileDeleteSerializer(serializers.Serializer):
    """Serializer for file deletion request"""

    bucket = serializers.CharField(
        required=True, help_text="Bucket name where the file is stored"
    )
    object_name = serializers.CharField(
        required=True, help_text="Object name to delete"
    )
