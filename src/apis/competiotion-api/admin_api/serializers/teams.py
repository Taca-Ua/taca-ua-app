"""
Team management serializers
"""

from rest_framework import serializers

from .courses import CourseListSerializer
from .modalities import ModalityListSerializer
from .students import StudentListSerializer


class TeamListRequestSerializer(serializers.Serializer):
    """Serializer for listing teams with filters"""

    modality_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)


class TeamListSerializer(serializers.Serializer):
    """Serializer for listing teams"""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    modality = ModalityListSerializer()
    course = CourseListSerializer()


class TeamDetailSerializer(TeamListSerializer):
    """Serializer for team details"""

    players = StudentListSerializer(many=True)


class TeamCreateSerializer(serializers.Serializer):
    """Serializer for creating a team"""

    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    modality_id = serializers.UUIDField(required=True)
    course_id = serializers.UUIDField(required=True)


class TeamUpdateSerializer(serializers.Serializer):
    """Serializer for updating a team"""

    name = serializers.CharField(required=False, allow_blank=True)
    modality_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)
    players_add = serializers.ListField(child=serializers.UUIDField(), required=False)
    players_remove = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )
