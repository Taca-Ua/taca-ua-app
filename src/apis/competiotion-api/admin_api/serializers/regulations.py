"""
Regulation management serializers
"""

from rest_framework import serializers


class RegulationListSerializer(serializers.Serializer):
    """Serializer for listing regulations"""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    modality_id = serializers.IntegerField()
    file_url = serializers.URLField(read_only=True)
    file_hash = serializers.CharField(read_only=True)
    file_size = serializers.IntegerField(read_only=True, required=False)
    already_exists = serializers.BooleanField(read_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)


class RegulationCreateSerializer(serializers.Serializer):
    """Serializer for creating a new regulation"""

    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    modality_id = serializers.IntegerField(required=True)
    file = serializers.FileField(
        required=True,
        help_text="PDF file of the regulation",
    )

    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size cannot exceed {max_size / (1024 * 1024)}MB"
            )

        # Check file extension
        allowed_extensions = [".pdf", ".doc", ".docx"]
        file_extension = value.name.split(".")[-1].lower()
        if f".{file_extension}" not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type .{file_extension} is not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )

        return value


class RegulationUpdateSerializer(serializers.Serializer):
    """Serializer for updating regulation metadata"""

    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    modality_id = serializers.IntegerField(required=False)
    file = serializers.FileField(
        required=False,
        help_text="New PDF file to replace existing regulation",
    )

    def validate_file(self, value):
        """Validate uploaded file"""
        if value:
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"File size cannot exceed {max_size / (1024 * 1024)}MB"
                )

            # Check file extension
            allowed_extensions = [".pdf", ".doc", ".docx"]
            file_extension = value.name.split(".")[-1].lower()
            if f".{file_extension}" not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File type .{file_extension} is not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )

        return value
