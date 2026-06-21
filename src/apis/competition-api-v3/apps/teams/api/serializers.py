from rest_framework import serializers


# Helper serializers
class TeamModalitySummary(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class TeamCourseSummary(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    abbreviation = serializers.CharField()


class TeamPlayerSummary(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    student_number = serializers.CharField()


class TeamSeasonSummary(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


# Response serializers
class TeamListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    modality = TeamModalitySummary()
    course = TeamCourseSummary()
    logo_url = serializers.CharField(allow_null=True, required=False)


class TeamDetailSerializer(TeamListSerializer):
    athletes = TeamPlayerSummary(many=True)
    season = TeamSeasonSummary()


# Request serializers
class TeamCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    modality_id = serializers.UUIDField(required=True)
    course_id = serializers.UUIDField(required=True)
    season_id = serializers.IntegerField(required=False)


class TeamUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)


class TeamAthleteUpdateSerializer(serializers.Serializer):
    athlete_ids = serializers.ListField(
        child=serializers.UUIDField(), required=True, allow_empty=False
    )
