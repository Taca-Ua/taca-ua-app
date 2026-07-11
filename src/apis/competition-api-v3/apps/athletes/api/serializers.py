from apps.utils import ExtensionSensitiveFileField
from rest_framework import serializers


# Helpers
class _CourseSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


# Response serializers for athletes module
class AthleteListSerializer(serializers.Serializer):
    """Serializer for listing students"""

    id = serializers.UUIDField()
    name = serializers.CharField()

    course = _CourseSummarySerializer()
    student_number = serializers.CharField()
    is_member = serializers.BooleanField(default=False)


class AthleteDetailSerializer(AthleteListSerializer):
    """Serializer for student detail"""

    course_proof_file_url = serializers.CharField()
    payment_proof_file_url = serializers.CharField()


# Request serializers for athletes module
class AthleteCreateSerializer(serializers.Serializer):
    """Serializer for creating a student"""

    name = serializers.CharField(required=True)
    course_id = serializers.UUIDField(required=True)
    student_number = serializers.CharField(required=True)
    is_member = serializers.BooleanField(required=False, default=False)
    course_proof = ExtensionSensitiveFileField(
        required=False, allow_null=True, allowed_extensions=[".pdf"]
    )
    payment_proof = ExtensionSensitiveFileField(
        required=False, allow_null=True, allowed_extensions=[".pdf"]
    )


class AthleteUpdateSerializer(serializers.Serializer):
    """Serializer for updating a student"""

    name = serializers.CharField(required=False)
    course_id = serializers.UUIDField(required=False)
    student_number = serializers.CharField(required=False)
    is_member = serializers.BooleanField(required=False)

    course_proof = ExtensionSensitiveFileField(
        required=False, allow_null=True, allowed_extensions=[".pdf"]
    )
    course_proof_deleted = serializers.BooleanField(required=False, default=False)

    payment_proof = ExtensionSensitiveFileField(
        required=False, allow_null=True, allowed_extensions=[".pdf"]
    )
    payment_proof_deleted = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        # Ensure that if a file is provided, the corresponding deleted flag is not set to True
        if attrs.get("course_proof") and attrs.get("course_proof_deleted"):
            raise serializers.ValidationError(
                "Cannot provide a course proof file and mark it as deleted at the same time."
            )
        if attrs.get("payment_proof") and attrs.get("payment_proof_deleted"):
            raise serializers.ValidationError(
                "Cannot provide a payment proof file and mark it as deleted at the same time."
            )
        return attrs


class AthleteMembershipSyncSerializer(serializers.Serializer):
    """Lista de NMECs a marcar como sócios (após reset a todos no âmbito)."""

    student_numbers = serializers.ListField(
        child=serializers.CharField(max_length=64, allow_blank=True),
        required=False,
        allow_empty=True,
    )
