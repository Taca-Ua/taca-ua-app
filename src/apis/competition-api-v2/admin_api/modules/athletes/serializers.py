from rest_framework import serializers


# Helpers
class _CourseSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    abbreviation = serializers.CharField()


# Response serializers for athletes module
class AthleteListSerializer(serializers.Serializer):
    """Serializer for listing students"""

    id = serializers.UUIDField()
    full_name = serializers.CharField()

    course = _CourseSummarySerializer()
    student_number = serializers.CharField()
    is_member = serializers.BooleanField(default=False)


class AthleteDetailSerializer(AthleteListSerializer):
    """Serializer for student detail"""

    pass


# Request serializers for athletes module
class AthleteListRequestSerializer(serializers.Serializer):
    """Serializer for listing students request parameters"""

    course_id = serializers.UUIDField(required=False)


class AthleteCreateSerializer(serializers.Serializer):
    """Serializer for creating a student"""

    full_name = serializers.CharField(required=True)
    course_id = serializers.UUIDField(required=True)
    student_number = serializers.CharField(required=True)
    is_member = serializers.BooleanField(required=False, default=False)


class AthleteUpdateSerializer(serializers.Serializer):
    """Serializer for updating a student"""

    full_name = serializers.CharField(required=False)
    course_id = serializers.UUIDField(required=False)
    student_number = serializers.CharField(required=False)
    is_member = serializers.BooleanField(required=False)


class AthleteMembershipSyncSerializer(serializers.Serializer):
    """Lista de NMECs a marcar como sócios (após reset a todos no âmbito)."""

    student_numbers = serializers.ListField(
        child=serializers.CharField(max_length=64, allow_blank=True),
        required=False,
        allow_empty=True,
    )
