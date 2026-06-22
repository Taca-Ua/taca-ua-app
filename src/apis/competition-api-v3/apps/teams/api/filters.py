from rest_framework import serializers


class TeamListRequestSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(required=False)
    modality_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)
    nucleus_id = serializers.UUIDField(required=False)
