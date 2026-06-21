from rest_framework import serializers


class AthleteListRequestSerializer(serializers.Serializer):
    """Serializer for listing students request parameters"""

    course_id = serializers.UUIDField(required=False)
    team_id = serializers.UUIDField(required=False)
